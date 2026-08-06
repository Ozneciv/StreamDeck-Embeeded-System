# 🎛️ StreamDeck-Embeeded-System

<p align="center">
  <img src="streamdeck_hardware.png" alt="StreamDeck Hardware STM32 BluePill Pronto" height="380" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); margin-right: 12px; vertical-align: middle;">
  <img src="streamdeck_assembly.jpg" alt="StreamDeck Processo de Montagem e Soldagem" height="380" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); vertical-align: middle;">
</p>

<p align="center">
  <strong>Macro Pad Físico de 9 Botões baseado em STM32F103C8T6 (BluePill) e USB Custom HID</strong><br>
  Varredura por <strong>Interrupção de Timer de Hardware (TIM2 a 100 Hz)</strong> e <strong>PCB Face Simples Manual (B.Cu)</strong><br>
  Interface de controle e simulação desenvolvida em <strong>Python 3 (Tkinter / Web Engine)</strong><br>
  Projeto acadêmico para a disciplina de <strong>Sistemas Embarcados I</strong><br>
  <strong>FEELT</strong> — Faculdade de Engenharia Elétrica | <strong>UFU</strong> — Universidade Federal de Uberlândia
</p>

---

## 👥 Integrantes do Projeto

| Nome | Matrícula | Curso |
| :--- | :---: | :---: |
| **Vicenzo De Marco Olivalves** | `12421ECP006` | Engenharia de Computação |
| **Bruna de Jesus Silva** | `12021ETE007` | Engenharia Eletrônica |
| **Gustavo Martins Ribeiro Moura** | `12111ETE002` | Engenharia Eletrônica |
| **Mateus Henrique Gonçalves** | `12311ECP021` | Engenharia de Computação |

---

## 📌 Visão Geral do Projeto

O **StreamDeck-Embeeded-System** é um dispositivo de entrada físico (*Macro Pad*) composto por uma matriz 3x3 de chaves mecânicas soldadas manualmente em uma placa de circuito impresso de **face simples (Single-Layer B.Cu)** com trilhas reforçadas ($0.8\,\text{mm}$ a $1.2\,\text{mm}$) otimizada para corrosão manual. O controle do sistema é realizado pelo microcontrolador **STM32F103C8T6 (ARM Cortex-M3 @ 72 MHz)** executando um firmware em C de baixo nível no **STM32CubeIDE**.

### 🚀 Diferenciais de Firmware & Hardware:
* ⚡ **Zero Polling no Loop Principal:** O firmware opera 100% sob **Interrupção de Hardware por Timer (TIM2 a 100 Hz / 10 ms)** com `HAL_TIM_PeriodElapsedCallback()`. A CPU permanece em modo de baixo consumo `__WFI()` (Wait For Interrupt) quando ociosa.
* 🛡️ **Debouncing por Máquina de Estados:** Filtro temporal não-bloqueante de 40 ms executado diretamente dentro da rotina de interrupção ISR.
* 🏬 **PCB Face Simples para Confecção Manual:** Roteamento em camada única (`B.Cu`) com trilhas espessas de $0.8\,\text{mm}$ a $1.2\,\text{mm}$, projetado para o método artesanal de transferência térmica e corrosão em Percloreto de Ferro.
* 🔄 **Comunicação USB HID Bidirecional:** Transmissão de pacotes IN (scancodes F13 a F21) e recepção de pacotes OUT do hospedeiro para atualização de status em tempo real.
* 📄 **Relatório Técnico em LaTeX:** Relatório acadêmico completo nos padrões UFU/FEELT (`relatorio_streamdeck.tex` e `RELATORIO_STREAMDECK_UFU.pdf`).

---

## 🛠️ Especificações Técnicas de Hardware & Firmware

* **Microcontrolador:** STM32F103C8T6 (ARM Cortex-M3, 32-bit).
* **Frequência da CPU (SYSCLK):** 72 MHz (Cristal HSE 8 MHz × PLL 9).
* **Frequência USB (USBCLK):** 48 MHz (Divisor PLL 1.5).
* **Topologia de Entrada:** Matriz Multiplexada 3x3 (3 Linhas Open Drain × 3 Colunas PullUp).
* **Interrupção de Hardware:** Timer TIM2 configurado com prescaler 7199 (10 kHz tick) e período 99 (100 Hz / 10 ms ISR).
* **Debouncing:** Filtro temporal por máquina de estados em ISR (janela de 40 ms).
* **Pacote USB HID:** Relatório padrão de 8 Bytes (Byte 2 = `0x68 + tecla_id`).

---

## 🏬 Placa de Circuito Impresso (PCB Face Simples KiCad)

O projeto inclui a placa de circuito impresso desenvolvida no **KiCad**, localizada no diretório [`PCB/PCB_macropad/`](file:///c:/Users/vicen/Downloads/streamdeck/PCB/PCB_macropad):

* 📄 **Esquemático Eletrônico (PDF):** [`PCB/PCB_macropad/sch_macropad_plote.pdf`](file:///c:/Users/vicen/Downloads/streamdeck/PCB/PCB_macropad/sch_macropad_plote.pdf)
* 📐 **Arquivos de Projeto KiCad:** `PCB_macropad.kicad_sch` e `PCB_macropad.kicad_pcb`
* 🏭 **Gerber Files para Fabricação:** Pasta [`PCB/PCB_macropad/gerber/`](file:///c:/Users/vicen/Downloads/streamdeck/PCB/PCB_macropad/gerber).

---

## 🐍 Como Executar a Interface Python

A aplicação de acompanhamento é executada via **Python 3**:

```bash
python app.py
```

---

## 📂 Estrutura do Repositório

```text
StreamDeck-Embeeded-System/
├── relatorio_streamdeck.tex   # Relatório Técnico em LaTeX (Formatação ABNT / UFU / IEEE)
├── RELATORIO_STREAMDECK_UFU.pdf # Relatório impresso em PDF pronto para submissão
├── app.py                    # Aplicação de Servidor em Python 3
├── streamdeck bluepill/      # Projeto em C no STM32CubeIDE (Firmware com Interrupção TIM2)
│   ├── Core/
│   │   ├── Inc/              # Cabeçalhos main.h, usb_device.h, etc.
│   │   └── Src/
│   │       ├── main.c        # Firmware com TIM2 ISR, debouncing e USB HID
│   │       └── ...
│   ├── USB_DEVICE/           # Pilha USB Device Custom HID da ST
│   └── streamdeck bluepill.ioc # Configuração do projeto no STM32CubeMX
├── PCB/                      # Projeto da PCB Face Simples para confecção manual (KiCad)
│   └── PCB_macropad/
│       ├── PCB_macropad.kicad_pcb # Layout Single-Layer B.Cu com trilhas de 0.8mm
│       └── gerber/           # Gerbers para corrosão manual
├── dashboard/                # Interface Gráfica da Aplicação Python
├── streamdeck_hardware.png   # Foto do hardware finalizado
└── streamdeck_assembly.jpg   # Foto do processo de soldagem e montagem
```

---

<p align="center">
  Desenvolvido com 💙 pela equipe de Engenharia da <strong>FEELT / UFU</strong> — 2026.
</p>
