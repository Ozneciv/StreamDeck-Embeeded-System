/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Firmware principal do Stream Deck (Sistemas Embarcados - FEELT / UFU)
  * @details        : Executa a varredura da matriz 3x3 ativada por Interrupção de Hardware
  *                   via Timer TIM2 (100Hz / 10ms) e transmite relatórios USB Custom HID 
  *                   (Scancodes F13 a F21) sem uso de polling no loop principal.
  * @authors        : Vicenzo De Marco Olivalves (12421ECP006)
  *                   Bruna de Jesus Silva (12021ETE007)
  *                   Gustavo Martins Ribeiro Moura (12111ETE002)
  *                   Matheus Henrique Gonçalves (12311ECP021)
  * @date           : 2026-08-06
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_device.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "usbd_customhid.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
/**
 * @brief Estrutura de dados para controle da Matriz e Debouncing não-bloqueante por ISR.
 */
typedef struct {
    volatile int last_raw_key;     /*!< Última tecla detectada na varredura física (-1 a 8) */
    volatile int stable_valid_key; /*!< Tecla confirmada após a janela de debouncing */
    volatile uint32_t sample_ticks;/*!< Contador de amostras em ms ativado via Timer ISR */
} StreamDeck_State_t;
/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define DEBOUNCE_THRESHOLD_MS 40   /*!< Janela de estabilização do ruído mecânico em ms */
#define SCAN_TIMER_PERIOD_MS  10   /*!< Período de interrupção do Timer TIM2 (100 Hz) */
#define USB_HID_SCANCODE_F13  0x68 /*!< Código Hexadecimal da tecla F13 no padrão USB HID */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */
/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
TIM_HandleTypeDef htim2;

/* USER CODE BEGIN PV */
extern USBD_HandleTypeDef hUsbDeviceFS;

/** @brief Mapeamento físico dos pinos das Linhas (PA1, PA2, PA3 - Open Drain Out) */
static uint16_t rowPins[3] = {GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3};
static GPIO_TypeDef* rowPorts[3] = {GPIOA, GPIOA, GPIOA};

/** @brief Mapeamento físico dos pinos das Colunas (PA4, PA5, PA6 - Input PullUp) */
static uint16_t colPins[3] = {GPIO_PIN_4, GPIO_PIN_5, GPIO_PIN_6};
static GPIO_TypeDef* colPorts[3] = {GPIOA, GPIOA, GPIOA};

/** @brief Instância global da máquina de estados do Stream Deck */
static volatile StreamDeck_State_t deck_state = {
    .last_raw_key = -1,
    .stable_valid_key = -1,
    .sample_ticks = 0
};
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_TIM2_Init(void);
/* USER CODE BEGIN PFP */
int scanMatrix_ISR(void);
void enviarReportUSB(int tecla_id);
void processDebounce_ISR(void);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/**
  * @brief  Varre a matriz de teclas 3x3.
  * @note   Função otimizada executada dentro do contexto de Interrupção por Hardware (Timer ISR).
  * @retval ID da tecla acionada (0 a 8) ou -1 se nenhuma tecla estiver pressionada.
  */
int scanMatrix_ISR(void) {
    for (int r = 0; r < 3; r++) {
        // Coloca a linha atual em nível LÓGICO BAIXO (0V / RESET)
        HAL_GPIO_WritePin(rowPorts[r], rowPins[r], GPIO_PIN_RESET);

        // Estabilização de sinal para capacitância das trilhas da PCB
        for (volatile int i = 0; i < 50; i++) { __NOP(); }

        for (int c = 0; c < 3; c++) {
            // Se a coluna ler 0V, o switch daquela interseção (r, c) foi fechado
            if (HAL_GPIO_ReadPin(colPorts[c], colPins[c]) == GPIO_PIN_RESET) {
                // Restaura a linha para Alta Impedância (SET / Open-Drain Hi-Z)
                HAL_GPIO_WritePin(rowPorts[r], rowPins[r], GPIO_PIN_SET);
                return (r * 3) + c; // Retorna o índice de 0 a 8
            }
        }
        // Restaura a linha para Alta Impedância antes de testar a próxima
        HAL_GPIO_WritePin(rowPorts[r], rowPins[r], GPIO_PIN_SET);
    }
    return -1; // Nenhuma tecla pressionada
}

/**
  * @brief  Constrói e envia o pacote de 8 Bytes USB HID para o computador host.
  * @param  tecla_id ID da tecla (0 a 8) ou -1 para liberada (Release).
  * @retval None
  */
void enviarReportUSB(int tecla_id) {
    uint8_t hid_report[8] = {0}; // Array de 8 bytes no padrão USB HID Keyboard Report

    if (tecla_id != -1) {
        // Byte 0: Teclas modificadoras (Ctrl, Shift, Alt, GUI) -> 0x00
        // Byte 1: Reservado -> 0x00
        // Byte 2: Scancode da tecla primária -> F13 (0x68) + ID
        hid_report[2] = USB_HID_SCANCODE_F13 + tecla_id;
    }

    // Envia o relatório de 8 bytes via EndPoint EP1 IN (Interrupt Transmission)
    USBD_CUSTOM_HID_SendReport(&hUsbDeviceFS, hid_report, sizeof(hid_report));
}

/**
  * @brief  Filtro de Debouncing executado periodicamente a cada estouro do Timer TIM2.
  * @note   Substitui totalmente o Polling. Garante imunidade a ruídos sem bloquear a CPU.
  * @retval None
  */
void processDebounce_ISR(void) {
    int current_key = scanMatrix_ISR();

    if (current_key != deck_state.last_raw_key) {
        deck_state.sample_ticks = HAL_GetTick();
        deck_state.last_raw_key = current_key;
    }

    // Se o sinal se manteve estável durante a janela de 40ms
    if ((HAL_GetTick() - deck_state.sample_ticks) >= DEBOUNCE_THRESHOLD_MS) {
        if (current_key != deck_state.stable_valid_key) {
            deck_state.stable_valid_key = current_key;
            enviarReportUSB(deck_state.stable_valid_key);
        }
    }
}

/**
  * @brief  Callback de Interrupção por Estouro do Timer (TIM2 ISR).
  * @param  htim Ponteiro para o handle do timer que gerou a interrupção.
  * @retval None
  */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM2) {
        // Processa a varredura e o debouncing em tempo real por interrupção
        processDebounce_ISR();
    }
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */
  /* Força a Re-enumeração USB no Windows (Reset no D+ / PA12) */
  GPIO_InitTypeDef GPIO_InitStruct_USB = {0};
  __HAL_RCC_GPIOA_CLK_ENABLE();
  GPIO_InitStruct_USB.Pin = GPIO_PIN_12;
  GPIO_InitStruct_USB.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct_USB.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct_USB);
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_12, GPIO_PIN_RESET);
  HAL_Delay(100);
  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USB_DEVICE_Init();
  MX_TIM2_Init();
  /* USER CODE BEGIN 2 */
  /* Habilita o sinal de depuração ST-LINK mesmo quando a CPU entra em repouso (__WFI) */
  HAL_DBGMCU_EnableDBGSleepMode();

  /* Inicia o Timer TIM2 com Interrupção de Hardware ativada (100 Hz / 10ms) */
  HAL_TIM_Base_Start_IT(&htim2);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
    // __WFI(); // Comentado para permitir leitura ao vivo (Live Expressions) via ST-LINK
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USB;
  PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_PLL_DIV1_5;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 7199;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 99;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, LINE_1_Pin|LINE_2_Pin|LINE_3_Pin, GPIO_PIN_SET);

  /*Configure GPIO pins : LINE_1_Pin LINE_2_Pin LINE_3_Pin */
  GPIO_InitStruct.Pin = LINE_1_Pin|LINE_2_Pin|LINE_3_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pins : COL_1_Pin COL_2_Pin COL_3_Pin */
  GPIO_InitStruct.Pin = COL_1_Pin|COL_2_Pin|COL_3_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
