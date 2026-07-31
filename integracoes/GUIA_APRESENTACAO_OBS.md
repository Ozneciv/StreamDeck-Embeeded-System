# 🎛️ Guia Completo de Simulação & Apresentação do Stream Deck STM32 BluePill

Este guia contém o passo a passo para demonstrar com sucesso o **Stream Deck Embarcado** na sala de aula, integrando o hardware físico STM32, o **Dashboard Web Interativo (com Análise Técnica)**, scripts de automação do Windows e o **OBS Studio**.

---

## 📐 1. Mapeamento de Hardware & Teclas (Matriz 3x3)

O firmware gravado no STM32 BluePill (`main.c`) varre as 3 linhas e 3 colunas via varredura multiplexada GPIO e envia pacotes **USB Custom HID (8 bytes)** com as teclas estendidas de **F13 a F21**:

| Botão | Tecla HID | Hex Code | Linha (GND Out) | Coluna (PullUp In) | Ação no Dashboard Web |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | **F13** | `0x68` | PA1 | PA4 | Efeito Sonoro / Vinheta (Soundboard) |
| **#2** | **F14** | `0x69` | PA1 | PA5 | Mutar / Desmutar Microfone (On-Air) |
| **#3** | **F15** | `0x6A` | PA1 | PA6 | Alternar Cenas da Apresentação |
| **#4** | **F16** | `0x6B` | PA2 | PA4 | Iniciar / Pausar Cronômetro |
| **#5** | **F17** | `0x6C` | PA2 | PA5 | Disparar Alerta em Tela Cheia para a Sala |
| **#6** | **F18** | `0x6D` | PA2 | PA6 | Efeitos Visuais de LED / Temas |
| **#7** | **F19** | `0x6E` | PA3 | PA4 | Diagrama de Arquitetura da STM32 |
| **#8** | **F20** | `0x6F` | PA3 | PA5 | Gerador de Memes de Embarcados |
| **#9** | **F21** | `0x70` | PA3 | PA6 | Celebração Final com Confetes & Fanfarra |

---

## 📊 2. Explicação Detalhada de Cada Painel do Dashboard Web

Quando você clica no botão **`🔬 Análise Técnica`**, o Dashboard exibe 5 painéis de engenharia. Veja o que cada um significa para explicar na apresentação:

### 1. 🔌 Telemetria de Pinos (GPIO)
- **O que é:** Mostra o estado lógico em tempo real das portas do microcontrolador (GPIOA).
- **Linhas (PA1, PA2, PA3 - Open-Drain Output):** O firmware força sequencialmente cada uma das 3 linhas para Nível Lógico Baixo (`0V / RESET`), mantendo as outras duas em Alta Impedância (*Hi-Z*). A linha ativa é destacada em rosa/vermelho.
- **Colunas (PA4, PA5, PA6 - Input Pull-Up):** As colunas ficam normalmente alimentadas em `3.3V` pelos resistores de *Pull-Up* internos da STM32. Quando um botão físico conecta uma linha à coluna, a coluna cai para `0V (GND)` e é destacada em verde.

### 2. 📈 Analisador Lógico de Sinais (GPIO Waves)
- **O que é:** Um gráfico em forma de onda de pulso digital (*Digital Pulse Waveform*) simulando a saída de um osciloscópio conectado aos pinos da placa.
- **Linha Rosa (Output):** Mostra a transição da linha ativada de `3.3V` para `0V (GND)` durante o ciclo de varredura multiplexada.
- **Linha Verde (Input):** Mostra a queda de tensão no pino de entrada da coluna no momento exato do fechamento do contato mecânico do botão (borda de descida / *falling edge*).

### 3. 📦 Inspeção de Pacote USB HID (8 Bytes)
- **O que é:** Exibe a estrutura exata do buffer de memória enviado pela STM32 para o barramento USB (`USBD_CUSTOM_HID_SendReport`).
- **Detalhamento dos Bytes:**
  - `Byte 0 (Modifier Keys)`: Teclas modificadoras (Ctrl, Alt, Shift). Fica em `0x00`.
  - `Byte 1 (Reserved)`: Reservado pela especificação USB HID (`0x00`).
  - `Byte 2 (Key Array - Slot 1)`: É onde a STM32 coloca o código hexadecimal da tecla. Como F13 equivale a `0x68` na tabela HID USB, somamos o ID do botão (`0x68 + tecla_id`), enviando de `0x68` (F13) até `0x70` (F21).
  - `Bytes 3 a 7`: Permitem enviar até mais 5 teclas simultâneas (*N-Key Rollover*).
- **Endpoint Info:** Mostra o envio via Endpoint **EP1 IN** por interrupção USB a cada 10ms.

### 4. 🛡️ Máquina de Estados do Debounce (40ms Window)
- **O que é:** O algoritmo de filtragem por software do ruído mecânico das chaves (*mechanical contact bounce*).
- **Trepidações Ignoradas (Bounces):** Botões mecânicos "quicam" eletricamente durante 5ms a 15ms ao serem apertados, gerando dezenas de transições falsas. O contador contabiliza os ruídos descartados.
- **Acionamentos Válidos:** Incrementado quando a função `debounceKey()` no `main.c` confirma que o pino manteve a mesma tecla de forma **estável por mais de 40 milissegundos** via `HAL_GetTick()`.

### 5. ⚙️ Registradores & Memória Flash / SRAM
- **O que é:** O mapa de recursos e ocupação de memória do chip ARM Cortex-M3 (STM32F103C8T6):
  - **Memória Flash (64 KB):** Ocupa ~14.8 KB (23%), contendo o código firmware compilado, pilha USB Device e a HAL.
  - **SRAM (20 KB):** Ocupa ~2.9 KB (14%), contendo as variáveis globais (`debounce_time`, `last_key`, `valid_key`) e a pilha de execução de funções.
  - **SYSCLK (72 MHz):** Frequência da CPU gerada pelo multiplicador PLL (Cristal HSE 8MHz × 9).
  - **USBCLK (48 MHz):** Frequência dedicada à USB gerada pela divisão por 1.5 do PLL (`72MHz / 1.5 = 48MHz`).
  - **GPIOA_CRL (`0x44333333`):** Valor do registrador de configuração da GPIOA (PA1..PA3 em Open-Drain e PA4..PA6 em Input Pull-Up).

---

## 🎯 3. Perguntas Esperadas do Professor (Alinhadas ao Conteúdo da Disciplina)

### ❓ 1. "Por que usaram Polling no `while(1)` em vez de Interrupções EXTI (External Interrupts)?"
> **Resposta:** Para uma matriz multiplexada (3x3), se usássemos interrupções EXTI nas colunas, ainda seria necessário desabilitar a EXTI e varrer as linhas manualmente para saber qual botão foi apertado. Além disso, debouncing dentro de uma ISR com atrasos bloqueantes corromperia o empilhamento de contexto do NVIC (*stacking/unstacking*). A varredura por Polling no `while(1)` com `HAL_GetTick()` realiza um debouncing **não-bloqueante** estável.

### ❓ 2. "Por que a linha é configurada em Open-Drain (`GPIO_MODE_OUTPUT_OD`) e não Push-Pull?"
> **Resposta:** O modo `Open-Drain` evita curto-circuito. Se duas teclas da mesma coluna fossem pressionadas ao mesmo tempo e as linhas estivessem em Push-Pull (uma em 3.3V e outra em 0V), haveria um curto direto entre VCC e GND. No modo Open-Drain, a linha ativa vai para `0V (GND)` e as inativas ficam em alta impedância (`Hi-Z`), eliminando qualquer risco de curto.

### ❓ 3. "Como otimizar a escrita de pinos evitando condições de corrida (BSRR vs ODR)?"
> **Resposta:** Usaríamos o registrador **`GPIOx_BSRR`** (Bit Set/Reset Register). Diferente do `GPIOx_ODR` (que exige a sequência de leitura-modificação-escrita `ODR |= (1<<x)` suscetível a condições de corrida se ocorrer uma interrupção concorrente), o `BSRR` executa a alteração do pino em uma **única instrução de escrita atômica** de 32 bits.

### ❓ 4. "Qual a diferença entre a comunicação do Stream Deck (USB Custom HID) e uma USART/UART?"
> **Resposta:** A USART/UART é serial assíncrona pino-a-pino que envia quadros de bits sob Baud Rates fixos e exige um conversor USB-Serial (FT232/CH340). O Stream Deck usa o periférico USB nativo da STM32 (PA11/PA12) sob a classe **USB Custom HID**. O Windows reconhece o dispositivo diretamente como um teclado Plug-and-Play genérico, enviando scancodes nativos de F13 a F21 sem necessitar de drivers ou de porta serial.

### ❓ 5. "Por que as variáveis `debounce_time`, `last_key` e `valid_key` foram declaradas como `volatile`?"
> **Resposta:** A palavra `volatile` instrui o compilador C a não aplicar otimizações agressivas que mantenham os valores guardados em registradores da CPU ARM, forçando a leitura/escrita direta na memória SRAM a cada iteração, o que garante sincronismo para Debug em tempo real.

### ❓ 6. "Como é configurada a árvore de clocks para o periférico USB?"
> **Resposta:** O periférico USB Device exige um clock estável de **48 MHz**. O cristal HSE de **8 MHz** é multiplicado pelo PLL x9 gerando **72 MHz** (SYSCLK). O sinal é então dividido por 1.5 (`RCC_USBCLKSOURCE_PLL_DIV1_5`), entregando exatamente `72 MHz / 1.5 = 48 MHz` para a USB.

---

## 🌐 4. Como Usar o Dashboard Web Interativo (Projetor da Sala)

1. Abra a pasta `dashboard/` e dê um duplo clique no arquivo [`index.html`](file:///c:/Users/vicen/Downloads/streamdeck/dashboard/index.html) no seu navegador.
2. Clique no botão **`🔬 Análise Técnica`** no topo da tela para abrir o Osciloscópio / Analisador Lógico e a inspeção dos 8 Bytes USB.
3. Conecte a placa **STM32 BluePill via cabo Micro-USB** no computador.
4. Ao pressionar qualquer um dos 9 botões no seu Stream Deck físico, a página Web detectará a tecla de **F13 a F21** instantaneamente.

---

## 📽️ 5. Como Mapear o Stream Deck no OBS Studio

1. Abra o **OBS Studio**.
2. Vá em **Configurações** -> **Teclas de Atalho (Hotkeys)**.
3. Clique no campo de atalho da cena desejada e **pressione o botão físico do Stream Deck** (ex: Botão 3 envia **F15**).

---

## ⚙️ 6. Como Usar os Scripts do Windows (AutoHotkey & Python)

- **AutoHotkey v2 (`streamdeck_hotkeys.ahk`)**: [`streamdeck_hotkeys.ahk`](file:///c:/Users/vicen/Downloads/streamdeck/integracoes/streamdeck_hotkeys.ahk) para atalhos nativos do Windows.
- **Script Python (`streamdeck_listener.py`)**: `python integracoes/streamdeck_listener.py` para log de telemetria no terminal.
