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
  * @brief  Ponto de entrada do programa (Application Entry Point).
  * @retval int
  */
int main(void)
{
  /* MCU Configuration--------------------------------------------------------*/
  HAL_Init();

  /* Configuração da árvore de Clock (72 MHz SYSCLK / 48 MHz USBCLK) */
  SystemClock_Config();

  /* Inicialização dos Periféricos de GPIO, USB e Timer */
  MX_GPIO_Init();
  MX_USB_DEVICE_Init();
  MX_TIM2_Init();

  /* USER CODE BEGIN 2 */
  /* Inicia o Timer TIM2 com Interrupção de Hardware ativada (100 Hz / 10ms) */
  HAL_TIM_Base_Start_IT(&htim2);
  /* USER CODE END 2 */

  /* Loop Infinito Não-Bloqueante (CPU entra em modo de baixo consumo/WFI) */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
    // A varredura ocorre 100% por Interrupção de Timer (HAL_TIM_PeriodElapsedCallback).
    // A CPU aguarda a próxima interrupção sem gastar ciclos em Polling.
    __WFI(); // Wait For Interrupt
  }
  /* USER CODE END 3 */
}

/**
  * @brief Configuração da Árvore de Clock (72MHz CPU / 48MHz USB)
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9; // 8MHz * 9 = 72MHz
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

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
}

/**
  * @brief Configuração do Timer de Hardware TIM2 (100 Hz / 10 ms)
  * @retval None
  */
static void MX_TIM2_Init(void)
{
  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 7199; // Prescaler: 72MHz / 7200 = 10 kHz (0.1ms tick)
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 99;      // Period: 100 ticks = 10 ms (100 Hz ISR frequency)
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
  if (HAL_TIM_Ex_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief Configuração das Portas GPIO (PA1..PA3 Open Drain | PA4..PA6 Pull-Up)
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /* Linhas PA1, PA2, PA3 -> Output Open Drain (Hi-Z no nível 1, 0V no nível 0) */
  GPIO_InitStruct.Pin = GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3, GPIO_PIN_SET);

  /* Colunas PA4, PA5, PA6 -> Input com Pull-Up interno ativado */
  GPIO_InitStruct.Pin = GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_6;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
}

void Error_Handler(void)
{
  __disable_irq();
  while (1)
  {
  }
}
