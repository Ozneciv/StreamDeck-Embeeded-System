/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
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

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
extern USBD_HandleTypeDef hUsbDeviceFS;

// Mapeamento dos pinos (Linhas: PA1, PA2, PA3 | Colunas: PA4, PA5, PA6)
uint16_t rowPins[3] = {GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3};
uint16_t colPins[3] = {GPIO_PIN_4, GPIO_PIN_5, GPIO_PIN_6};
GPIO_TypeDef* rowPorts[3] = {GPIOA, GPIOA, GPIOA};
GPIO_TypeDef* colPorts[3] = {GPIOA, GPIOA, GPIOA};

// Variáveis de controle do Debounce blindadas para o Debugger (volatile)
volatile uint32_t debounce_time = 0;
volatile int last_key = -1;
volatile int valid_key = -1;
/* USER CODE END PV */
/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
// 1. Função que varre a matriz 3x3
int scanMatrix(void) {
    for (int r = 0; r < 3; r++) {
        // Força a linha atual para GND (0V)
        HAL_GPIO_WritePin(rowPorts[r], rowPins[r], GPIO_PIN_RESET);

        for (int c = 0; c < 3; c++) {
            // Se ler 0, o botão daquela coluna foi pressionado
            if (HAL_GPIO_ReadPin(colPorts[c], colPins[c]) == GPIO_PIN_RESET) {
                // Devolve a linha para Hi-Z (Alta impedância) antes de sair
                HAL_GPIO_WritePin(rowPorts[r], rowPins[r], GPIO_PIN_SET);
                return (r * 3) + c;
            }
        }
        // Retorna a linha para Hi-Z antes de testar a próxima
        HAL_GPIO_WritePin(rowPorts[r], rowPins[r], GPIO_PIN_SET);
    }
    return -1; // Nenhuma tecla pressionada
}

// 2. Função de Envio USB
void enviarReportUSB(int tecla_id) {
    // Array OBRIGATÓRIO de 8 bytes para o descritor de teclado padrão
    uint8_t hid_report[8] = {0};

    if (tecla_id != -1) {
        // hid_report[0] = Modificadores (Ctrl/Alt/Shift) - Zerado
        // hid_report[1] = Reservado - Zerado
        // hid_report[2] até [7] = Teclas normais pressionadas

        // F13 começa no código hexadecimal 0x68.
        // Somando o ID (0 a 8), o Streamdeck enviará do F13 ao F21.
        hid_report[2] = 0x68 + tecla_id;
    }

    // Envia o pacote de 8 bytes para o barramento USB
    USBD_CUSTOM_HID_SendReport(&hUsbDeviceFS, hid_report, sizeof(hid_report));
}

// 3. Máquina de Estados para Debounce
void debounceKey(void) {
    int current_key = scanMatrix();

    // Reseta o contador de tempo caso o pino esteja "quicando"
    if (current_key != last_key) {
        debounce_time = HAL_GetTick();
        last_key = current_key;
    }

    // Confirma a leitura se o sinal se manteve estável por mais de 40ms
    if ((HAL_GetTick() - debounce_time) > 40) {
        if (current_key != valid_key) {
            valid_key = current_key;
            enviarReportUSB(valid_key);
        }
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

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USB_DEVICE_Init();
  /* USER CODE BEGIN 2 */

  /* USER CODE END 2 */

  /* Infinite loop */
    /* USER CODE BEGIN WHILE */
    while (1)
    {
      /* USER CODE END WHILE */

      /* USER CODE BEGIN 3 */
      debounceKey();
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
