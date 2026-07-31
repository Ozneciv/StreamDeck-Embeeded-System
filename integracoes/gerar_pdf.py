# -*- coding: utf-8 -*-
import os
import sys
from fpdf import FPDF

class PDFStudyGuide(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(35, 38, 121) # UFU Blue
        self.cell(0, 8, 'Stream Deck - Sistemas Embarcados - FEELT / UFU', new_x="LMARGIN", new_y="NEXT", align='L')
        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, 'GUIA COMPLETO DE ESTUDOS, ANATOMIA DO CODIGO E GABARITO DA BANCA', new_x="LMARGIN", new_y="NEXT", align='L')
        self.set_draw_color(35, 38, 121)
        self.set_line_width(0.8)
        self.line(10, 24, 200, 24)
        self.ln(5)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 8, f'Pagina {self.page_no()}/{{nb}} - Universidade Federal de Uberlandia (FEELT)', align='C')

def generate_pdf():
    pdf = PDFStudyGuide()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Team Section
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(35, 38, 121)
    pdf.cell(0, 7, 'Integrantes do Projeto:', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Helvetica', '', 9)
    members = [
        ("Vicenzo De Marco Olivalves", "12421ECP006"),
        ("Mateus Henrique Goncalves", "12311ECP021"),
        ("Gustavo Martins", "12111ETE002"),
        ("Bruna Silva", "12021ETE007")
    ]
    for name, reg in members:
        pdf.set_text_color(15, 23, 42)
        pdf.cell(90, 5, f"- {name}", new_x="RIGHT", new_y="TOP")
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(217, 119, 6)
        pdf.cell(0, 5, f"Matricula: {reg}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 9)

    pdf.ln(3)

    # Section 1: Matrix
    pdf.set_font('Helvetica', 'B', 11.5)
    pdf.set_text_color(35, 38, 121)
    pdf.cell(0, 7, '1. Mapeamento de Hardware & Teclas (Matriz 3x3)', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(0, 4.2, 'O firmware da STM32 BluePill (main.c) realiza varredura multiplexada continua na matriz 3x3 e envia pacotes USB Custom HID de 8 Bytes com scancodes de F13 a F21:')
    pdf.ln(2)

    # Table Header
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(35, 38, 121)
    pdf.cell(15, 6, 'Botao', 1, 0, 'C', True)
    pdf.cell(18, 6, 'Tecla HID', 1, 0, 'C', True)
    pdf.cell(18, 6, 'Hex Code', 1, 0, 'C', True)
    pdf.cell(24, 6, 'Linha (OD)', 1, 0, 'C', True)
    pdf.cell(25, 6, 'Coluna (PU)', 1, 0, 'C', True)
    pdf.cell(90, 6, 'Acao no Dashboard Web', 1, 1, 'L', True)

    # Table Rows
    pdf.set_font('Helvetica', '', 7.8)
    pdf.set_text_color(15, 23, 42)
    rows = [
        ("#1", "F13", "0x68", "PA1", "PA4", "Soundboard SFX (Sintetizador Web Audio)"),
        ("#2", "F14", "0x69", "PA1", "PA5", "Mudo / Desmudo Microfone (Estudio On-Air)"),
        ("#3", "F15", "0x6A", "PA1", "PA6", "Alternar Cenas (Slide / Webcam / STM32 Code)"),
        ("#4", "F16", "0x6B", "PA2", "PA4", "Iniciar / Pausar Cronometro da Apresentacao"),
        ("#5", "F17", "0x6C", "PA2", "PA5", "Alerta em Tela Cheia para a Sala de Aula"),
        ("#6", "F18", "0x6D", "PA2", "PA6", "Efeitos Visuais de Iluminacao LED"),
        ("#7", "F19", "0x6E", "PA3", "PA4", "Diagrama de Arquitetura da STM32 BluePill"),
        ("#8", "F20", "0x6F", "PA3", "PA5", "Gerador de Memes de Sistemas Embarcados"),
        ("#9", "F21", "0x70", "PA3", "PA6", "Celebracao Final com Confetes & Fanfarra")
    ]
    for b, k, h, r, c, a in rows:
        pdf.cell(15, 5.5, b, 1, 0, 'C')
        pdf.cell(18, 5.5, k, 1, 0, 'C')
        pdf.cell(18, 5.5, h, 1, 0, 'C')
        pdf.cell(24, 5.5, r, 1, 0, 'C')
        pdf.cell(25, 5.5, c, 1, 0, 'C')
        pdf.cell(90, 5.5, a, 1, 1, 'L')

    pdf.ln(3)

    # Section 2: Code Anatomy
    pdf.set_font('Helvetica', 'B', 11.5)
    pdf.set_text_color(35, 38, 121)
    pdf.cell(0, 7, '2. Anatomia Detalhada do Código C (main.c)', new_x="LMARGIN", new_y="NEXT")

    code_sections = [
        ("A. Funcao scanMatrix() - Linhas 69 a 86",
         "Converte coordenadas 2D da matriz para ID 1D via formula: (r * 3) + c. Forca a linha testada para 0V (RESET) e le a coluna. Antes de mudar de linha ou retornar, devolve a linha para GPIO_PIN_SET (Hi-Z no modo Open-Drain), garantindo que apenas uma linha fique em GND de cada vez."),
        ("B. Funcao enviarReportUSB(int tecla_id) - Linhas 89 a 105",
         "Cria um buffer uint8_t hid_report[8] = {0}. O Byte 2 carrega o scancode (0x68 + tecla_id), onde 0x68 e o codigo HID da tecla F13. Quando a tecla e solta (tecla_id == -1), envia o vetor zerado {0}, informando ao Windows a liberacao do botao."),
        ("C. Funcao debounceKey() - Linhas 108 a 124",
         "Filtro de temporizacao nao-bloqueante. Usa SysTick via HAL_GetTick(). Se a tecla mudo de estado, reseta debounce_time. Apenas confirma e dispara o envio USB se o sinal mantiver leitura estavel por mais de 40ms continuous.")
    ]

    for title, desc in code_sections:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(30, 58, 138) # Dark blue
        pdf.cell(0, 5, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 8.2)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 4, desc)
        pdf.ln(1.5)

    pdf.ln(2)

    # Section 3: Technical Analysis Panels
    pdf.set_font('Helvetica', 'B', 11.5)
    pdf.set_text_color(35, 38, 121)
    pdf.cell(0, 7, '3. Explicacao dos Painéis da Seção Analise Tecnica', new_x="LMARGIN", new_y="NEXT")

    panels = [
        ("1. Telemetria de Pinos GPIO (GPIOA)", "Linhas (PA1-PA3) atuam como Open-Drain (0V ativo). Colunas (PA4-PA6) sao entradas em Pull-Up (3.3V normalmente, caindo para 0V ao acionar o botao)."),
        ("2. Analisador Logico de Sinais (GPIO Waves)", "Simula a saida de um osciloscopio. Mostra a onda da linha ativada (0V) e a borda de descida (falling edge) da coluna no instante do clique."),
        ("3. Inspecao de Pacote USB HID (8 Bytes)", "Buffer enviado por USBD_CUSTOM_HID_SendReport. Byte 0 = Modificadores, Byte 1 = Reservado, Byte 2 = Scancode (0x68 + ID), Bytes 3..7 = Rollover. EP1 IN (10ms)."),
        ("4. Maquina de Estados do Debounce (40ms)", "Filtra ruídos mecanicos (contact bounce). O acionamento so e confirmado se o sinal mantiver leitura estavel por mais de 40ms via HAL_GetTick()."),
        ("5. Registradores & Memoria Flash / SRAM", "STM32F103C8T6. Flash (64KB): 14.8KB (23%), SRAM (20KB): 2.9KB (14%), SYSCLK: 72MHz, USBCLK: 48MHz (PLL/1.5). GPIOA_CRL = 0x44333333.")
    ]

    for title, desc in panels:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(21, 128, 61) # Green
        pdf.cell(0, 5, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 8.2)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 4, desc)
        pdf.ln(1.5)

    pdf.ln(2)

    # Section 4: Advanced Concepts & Enumeration
    pdf.set_font('Helvetica', 'B', 11.5)
    pdf.set_text_color(35, 38, 121)
    pdf.cell(0, 7, '4. Insights Avancados de Engenharia de Embarcados', new_x="LMARGIN", new_y="NEXT")

    insights = [
        ("Processo de Enumeracao USB (Full-Speed 12 Mbps)", "A BluePill possui resistor de Pull-Up de 1.5k no pino USB D+ (PA12). Ao plugar, eleva a linha para 3.3V. O Windows detecta, solicita os descritores (Get Descriptor) e carrega automaticamente o driver genérico hidusb.sys sem necessidade de instalação de driver externo."),
        ("Uso da palavra reservada 'volatile'", "As variaveis debounce_time, last_key e valid_key foram declaradas como volatile para impedir que o compilador GCC aplique otimizacoes mantendo valores em registradores da CPU, forçando a leitura/escrita direta na RAM a cada iteracao do SysTick."),
        ("Arvore de Clocks (Clock Tree)", "O cristal externo HSE de 8MHz e multiplicado pelo PLL x9 gerando 72MHz (SYSCLK). O barramento USB exige 48MHz, obtidos pelo divisor RCC_USBCLKSOURCE_PLL_DIV1_5 (72MHz / 1.5 = 48MHz).")
    ]

    for title, desc in insights:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(109, 40, 217) # Purple
        pdf.cell(0, 5, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 8.2)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 4, desc)
        pdf.ln(1.5)

    pdf.ln(2)

    # Section 5: Exam Q&A
    pdf.set_font('Helvetica', 'B', 11.5)
    pdf.set_text_color(35, 38, 121)
    pdf.cell(0, 7, '5. Perguntas da Banca / Prova (Gabarito Técnico Prof. Jeovane)', new_x="LMARGIN", new_y="NEXT")

    qas = [
        ("Q1. Por que usaram Polling no while(1) em vez de Interrupcoes EXTI?",
         "Em uma matriz multiplexada, usar EXTI nas colunas ainda exigiria varrer as linhas manualmente. Atrasos de debounce em uma ISR causariam estouro de contexto no NVIC (stacking/unstacking). O Polling com HAL_GetTick() e leve e nao-bloqueante."),
        ("Q2. Por que a linha e configurada em Open-Drain e nao Push-Pull?",
         "O modo Open-Drain evita curto-circuito. Se 2 teclas da mesma coluna fossem apertadas juntas e as linhas estivessem em Push-Pull (uma 3.3V e outra 0V), haveria um curto direto. Em Open-Drain, a linha ativa vai para 0V e as inativas ficam em alta impedancia (Hi-Z)."),
        ("Q3. Como otimizar a escrita de pinos evitando condicoes de corrida (BSRR vs ODR)?",
         "Usando o registrador GPIOx_BSRR. O registrador ODR exige a sequencia de leitura-modificacao-escrita (vulneravel a interrupcoes concorrentes), enquanto o BSRR executa a alteracao em uma unica instrucao de escrita atômica de 32 bits."),
        ("Q4. Qual a diferenca entre USB Custom HID e comunicacao USART/UART?",
         "A USART e serial assincrona com Baud Rate fixo que exige conversor serial. O Stream Deck usa a USB nativa da STM32 (PA11/PA12) sob a classe USB Custom HID. O Windows o reconhece diretamente como teclado Plug-and-Play (F13-F21)."),
        ("Q5. Por que as variaveis de controle foram declaradas como 'volatile'?",
         "A palavra volatile impede que o compilador C aplique otimizacoes mantendo os valores nos registradores da CPU ARM, forçando a leitura/escrita direta na SRAM a cada iteracao, garantindo sincronismo no Debugger."),
        ("Q6. Como e configurada a arvore de clocks para a USB?",
         "A USB exige 48 MHz. O cristal externo HSE de 8 MHz e multiplicado pelo PLL x9 gerando 72 MHz (SYSCLK). Esse sinal e dividido por 1.5 (RCC_USBCLKSOURCE_PLL_DIV1_5), entregando exatamente 48 MHz para o periférico USB.")
    ]

    for q, a in qas:
        pdf.set_font('Helvetica', 'B', 8.8)
        pdf.set_text_color(194, 65, 12) # Orange
        pdf.cell(0, 4.5, q, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 8.2)
        pdf.set_text_color(30, 41, 59)
        pdf.multi_cell(0, 4, a)
        pdf.ln(1.5)

    # Section 6: Future Improvements
    pdf.ln(2)
    pdf.set_font('Helvetica', 'B', 11.5)
    pdf.set_text_color(35, 38, 121)
    pdf.cell(0, 7, '6. Propostas de Expansao & Melhorias (Versao 2.0)', new_x="LMARGIN", new_y="NEXT")

    pdf.set_font('Helvetica', '', 8.2)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(0, 4, "1. Modo Sleep + EXTI: Colocar as colunas em interrupção EXTI_FALLING para permitir Sleep Mode no microcontrolador, acordando apenas ao apertar uma tecla.\n2. N-Key Rollover: Preencher os bytes hid_report[2] ate [7] para permitir atalhos com ate 6 teclas simultaneas.\n3. Displays OLED / Encoders: Adicionar encoders I2C para controle de volume e mini telas OLED para icones dinamicos.")

    output_path = os.path.join(os.getcwd(), 'GUIA_ESTUDO_STREAMDECK_UFU.pdf')
    pdf.output(output_path)
    print(f"PDF gerado com sucesso em: {output_path}")

if __name__ == '__main__':
    generate_pdf()
