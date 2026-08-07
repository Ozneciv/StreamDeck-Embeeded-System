# ⌨️ StreamDeck Embedded System

> Periférico de entrada dedicado (*Macro Pad / Stream Deck*) de 9 teclas mecânicas baseado no microcontrolador ARM Cortex-M3 (STM32F103C8T6), desenvolvido com arquitetura orientada a interrupção de timer (100 Hz), comunicação USB Custom HID nativa e PCB em camada única.

---

## 📌 Visão Geral

Este repositório contém o código-fonte do firmware em C (STM32CubeIDE), projeto de hardware no KiCad (PCB Single-Layer `B.Cu` e arquivos Gerber), modelos 3D em STL da carcaça e o relatório técnico para a disciplina de **Sistemas Embarcados I** da **Universidade Federal de Uberlândia (UFU / FEELT)**.

---

## 🌟 Principais Características

- **⚡ Zero Polling:** Varredura da matriz 3x3 realizada por **Interrupção por Timer de Hardware (TIM2 a 100 Hz / 10 ms)** com repouso em baixo consumo (`__WFI()`).
- **🔄 Re-enumeração USB Automática:** Reset de software no pino USB D+ (`PA12`) na inicialização para identificação instantânea no SO após gravações.
- **🛡️ Anti-Ghosting:** Matriz 3x3 associada a 9 diodos $1\text{N}4148$.
- **🔌 Classe USB Custom HID:** Envio nativo de relatórios IN de 8 Bytes com atalhos de teclado (F13 a F21) e suporte a relatórios OUT bidirecionais.
- **📐 PCB Face Simples:** Placa projetada no KiCad em camada única (`B.Cu`) com trilhas reforçadas ($0.8\,\text{mm}$ a $1.2\,\text{mm}$) para fabricação por corrosão artesanal.
- **📦 Carcaça 3D:** Gabinete personalizado impresso em 3D com insertos roscados M3.

---

## 📷 Fotos do Projeto

<div align="center">

| Protótipo Finalizado | Montagem Física Interna |
| :---: | :---: |
| ![Protótipo Finalizado](Projeto%20Pronto.jpeg) | ![Montagem Física](Montagem.jpeg) |

</div>

---

## 🔌 Mapeamento de Pinos (Pinout STM32F103C8T6)

| Pino | Função | Modo GPIO / Periférico |
| :---: | :---: | :---: |
| **PA1, PA2, PA3** | Linhas 1 a 3 da Matriz | `GPIO_MODE_OUTPUT_OD` (Open Drain) |
| **PA4, PA5, PA6** | Colunas 1 a 3 da Matriz | `GPIO_MODE_INPUT` (Pull-Up Interno) |
| **PA11 / PA12** | USB D- / USB D+ | Periférico USB Custom HID |
| **PA13 / PA14** | SWDIO / SWCLK | Interface de Gravação e Depuração ST-LINK |

---

## 📂 Estrutura do Repositório

```text
├── streamdeck bluepill/        # Projeto STM32CubeIDE (Firmware C e arquivo .ioc)
├── PCB_FINAL/                  # Arquivos de fabricação KiCad e Gerbers finais
├── 3D/                         # Arquivos e modelos 3D STL do gabinete e teclas
├── dashboard/                  # Painel web interativo para testes e telemetria
├── StreamDeck_SEMB.pdf         # Relatório Técnico & Memorial Descritivo (PDF)
├── relatorio_streamdeck.tex    # Código-fonte em LaTeX do relatório
└── README.md                   # Documentação do projeto
```

---

## 🛠️ Como Compilar e Gravar o Firmware

1. **Requisitos:**
   - [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html) (v1.10 ou superior)
   - Gravador ST-LINK V2 ou via USB DFU Bootloader
2. **Passos:**
   - Abra o STM32CubeIDE e importe a pasta `streamdeck bluepill`.
   - Compile o projeto (`Project -> Build Project` ou `Ctrl+B`).
   - Conecte o ST-LINK à placa Blue Pill (SWDIO: PA13, SWCLK: PA14, GND, 3.3V).
   - Clique em `Run -> Debug` ou `Flash` para gravar o arquivo `.elf`.

---

## 👥 Equipe (Discentes / FEELT UFU)

- **Bruna de Jesus Silva** — `12021ETE007`
- **Gustavo Martins Ribeiro Moura** — `12111ETE002`
- **Mateus Henrique Gonçalves** — `12311ECP021`
- **Vicenzo De Marco Olivalves** — `12421ECP006`

**Docente Responsável:** Prof. Jeovane Vicente de Sousa  
**Curso:** Engenharia de Computação & Engenharia Eletrônica — UFU / FEELT  
**Ano:** 2026
