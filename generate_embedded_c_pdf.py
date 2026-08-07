# -*- coding: utf-8 -*-
"""
==============================================================================
 GERADOR DO RELATÓRIO PDF DA ATIVIDADE DE EMBEDDED C (UFU / FEELT)
==============================================================================
 Compila o documento oficial da atividade de Embedded C (Partes 1 e 2)
 para o discente Vicenzo De Marco Olivalves (Engenharia de Computação / UFU).
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Capa

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#232679"))
        self.drawString(54, 800, "FEELT/UFU — RELATÓRIO DE ESTUDO EMBEDDED C (PARTES 1 E 2)")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))
        self.drawRightString(541, 800, "Sistemas Embarcados I")

        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(54, 792, 541, 792)

        # Rodapé
        self.line(54, 45, 541, 45)
        self.setFont("Helvetica", 9)
        self.drawString(54, 32, "Universidade Federal de Uberlândia — Faculdade de Engenharia Elétrica")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(541, 32, page_str)
        self.restoreState()

def build_pdf_activity(pdf_filename):
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#232679")
    c_dark = colors.HexColor("#0f143c")
    c_text = colors.HexColor("#1f2937")

    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary,
        alignment=1,
        spaceAfter=12
    )

    style_cover_sub = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_dark,
        alignment=1,
        spaceAfter=20
    )

    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_dark,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_text,
        alignment=4,
        firstLineIndent=30,
        spaceAfter=6
    )

    style_code = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f8fafc"),
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=0.5,
        borderPadding=8,
        spaceAfter=8
    )

    story = []

    # CAPA
    story.append(Spacer(1, 20))
    story.append(Paragraph("UNIVERSIDADE FEDERAL DE UBERLÂNDIA", ParagraphStyle('UFU', fontName='Helvetica-Bold', fontSize=13, alignment=1)))
    story.append(Paragraph("FACULDADE DE ENGENHARIA ELÉTRICA — FEELT", ParagraphStyle('FEELT', fontName='Helvetica-Bold', fontSize=10, alignment=1)))
    story.append(Paragraph("DISCIPLINA DE SISTEMAS EMBARCADOS I", ParagraphStyle('DISC', fontName='Helvetica', fontSize=9, alignment=1)))
    story.append(Spacer(1, 55))

    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=15))
    story.append(Paragraph("RESUMO TÉCNICO E CONCEITUAL", style_cover_title))
    story.append(Paragraph("PROGRAMAÇÃO EM C PARA SISTEMAS EMBARCADOS (EMBEDDED C) VS. COMPUTADORES", style_cover_sub))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=55))

    team_data = [
        [
            Paragraph("<b>Discente:</b><br/>Vicenzo De Marco Olivalves<br/>Matrícula: 12421ECP006", ParagraphStyle('TLeft', fontName='Helvetica', fontSize=10, leading=15)),
            Paragraph("<b>Docente Responsável:</b><br/>Prof. Jeovane Vicente de Sousa<br/><br/><b>Curso:</b><br/>Engenharia de Computação", ParagraphStyle('TRight', fontName='Helvetica', fontSize=10, leading=15))
        ]
    ]
    t_team = Table(team_data, colWidths=[240, 240])
    t_team.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 60))
    story.append(Paragraph("Uberlândia — MG<br/>2026", ParagraphStyle('Date', fontName='Helvetica', fontSize=9.5, alignment=1)))
    story.append(PageBreak())

    # APRESENTAÇÃO
    story.append(Paragraph("Apresentação", style_h1))
    pres_text = """
    Este documento apresenta o resumo dos conceitos abordados nas videoaulas de <i>Embedded C</i> (Partes 1 e 2) da disciplina de Sistemas Embarcados I da FEELT/UFU, ministrada pelo Prof. Jeovane Vicente de Sousa. O objetivo é discutir detalhadamente as particularidades da linguagem C quando aplicada ao desenvolvimento de firmware para microcontroladores (como o ARM Cortex-M3 / STM32F103), destacando as diferenças fundamentais em relação à programação C convencional para computadores de mesa (<i>desktops</i>), além de revisar tópicos essenciais como manipulação de registradores por operações bitwise, qualificadores de memória, estruturas, ponteiros e mapeamento de memória.
    """
    story.append(Paragraph(pres_text, style_body))
    story.append(Spacer(1, 15))

    # 1. INTRODUÇÃO
    story.append(Paragraph("1. Introdução", style_h1))
    story.append(Paragraph("Quando aprendemos a programar em C nos primeiros semestres do curso de Engenharia de Computação, geralmente escrevemos códigos que rodam sobre um Sistema Operacional (Windows, Linux ou macOS). Nesse ambiente, o sistema operacional abstrai o acesso ao hardware, gerencia a memória RAM de forma virtualizada e oferece uma quantidade quase ilimitada de recursos computacionais.", style_body))
    story.append(Paragraph("Porém, quando passamos para o desenvolvimento de Sistemas Embarcados (<i>Embedded C</i>), a realidade muda completamente. Na maioria das vezes, trabalhamos no modo <i>Bare-Metal</i> (sem sistema operacional), onde o nosso código roda diretamente sobre o silício do microcontrolador. Nesse contexto, o programador é o responsável direto por configurar cada pino de GPIO, ajustar os seletores de clock, inicializar os timers e manipular registradores específicos diretamente pelo endereço de memória física.", style_body))

    # 2. DIFERENÇAS
    story.append(Paragraph("2. Diferenças Fundamentais: C Convencional vs. Embedded C", style_h1))
    story.append(Paragraph("Abaixo estão destacadas as principais diferenças práticas que foram observadas durante o estudo das videoaulas e na prática de bancada com microcontroladores:", style_body))
    story.append(Paragraph("<b>1. Acesso Direto à Memória e Registradores (MMIO):</b> No PC, tentar acessar um endereço de memória física aleatório causa uma falha de segmentação (<i>Segmentation Fault</i>) barrada pelo SO. Em sistemas embarcados, a manipulação da placa é feita justamente apontando ponteiros diretamente para os endereços dos registradores mapeados em memória (<i>Memory-Mapped I/O</i>).", style_body))
    story.append(Paragraph("<b>2. Gerenciamento de Recursos (RAM e Flash):</b> Em um computador comum, temos gigabytes de RAM. No microcontrolador STM32F103C8T6 (Blue Pill), por exemplo, temos apenas 20 kB de SRAM e 64 kB de memória Flash. Alocação dinâmica de memória via <code>malloc()</code> e <code>free()</code> deve ser evitada ao máximo para não causar fragmentação de memória ou estouro de pilha (<i>stack overflow</i>).", style_body))
    story.append(Paragraph("<b>3. Ciclo de Vida do Programa e Loop Infinito:</b> Em C para PC, a função <code>main()</code> executa uma sequência de instruções e encerra retornando 0 para o SO. Em embarcados, o <code>main()</code> <b>nunca pode retornar</b>; após a inicialização dos periféricos, o código entra em um loop infinito (<code>while(1)</code>) para manter o dispositivo operando continuamente ou em repouso com instrução de baixo consumo (<code>__WFI()</code>).", style_body))
    story.append(Paragraph("<b>4. Determinismo de Tempo Real e Interrupções:</b> Enquanto no PC os programas disputam tempo de CPU via escalonador do SO, no microcontrolador eventos críticos de hardware acionam rotinas de interrupção (<i>Interrupt Service Routines</i> — ISR) tratadas instantaneamente via controlador de interrupção (ex.: NVIC no ARM Cortex-M).", style_body))

    # 3. REVISÃO DOS CONCEITOS
    story.append(Paragraph("3. Revisão Sistemática dos Conceitos de Linguagem C", style_h1))

    story.append(Paragraph("3.1 Variáveis, Escopo e Qualificadores Especiais", style_h2))
    story.append(Paragraph("A escolha correta dos qualificadores de variáveis é crítica no desenvolvimento de firmware:<br/>• <code>volatile</code>: O professor deu um grande destaque a este qualificador. Ele avisa ao compilador que o valor da variável pode ser alterado a qualquer momento fora do fluxo normal do código (por uma interrupção de hardware ou pela alteração física de um registrador). O <code>volatile</code> impede que o compilador faça otimizações indesejadas, como salvar o valor da variável em um registrador interno da CPU em vez de reler a RAM.<br/>• <code>const</code>: Informa que o valor da variável não pode ser alterado. Em microcontroladores, declarar vetores grandes ou tabelas como <code>const</code> faz com que eles fiquem salvos diretamente na memória <b>Flash ROM</b>, economizando a escassa memória RAM.<br/>• <code>static</code>: Quando aplicada a uma variável local, preserva seu valor entre chamadas sucessivas da função. Quando aplicada a uma variável global ou função, limita o seu escopo apenas ao arquivo <code>.c</code> onde foi declarada (encapsulamento de módulo).", style_body))

    story.append(Paragraph("3.2 Tipos Inteiros de Tamanho Fixo (<code>stdint.h</code>)", style_h2))
    story.append(Paragraph("Na programação embarcada, usar tipos genéricos como <code>int</code> pode gerar problemas graves de portabilidade, pois o tamanho em bytes do <code>int</code> muda conforme a arquitetura (pode ter 16 bits em um microcontrolador AVR de 8 bits ou 32 bits em um ARM). Por isso, utilizamos sempre a biblioteca <code>&lt;stdint.h&gt;</code>, declarando tipos de tamanho fixo bem definidos: <code>uint8_t</code> (8 bits sem sinal), <code>uint16_t</code> (16 bits sem sinal) e <code>uint32_t</code> (32 bits sem sinal). Isso bate exatamente com o tamanho dos registradores do STM32 (que são de 32 bits).", style_body))

    story.append(Paragraph("3.3 Operações Lógicas Bit a Bit (Bitwise Operators)", style_h2))
    story.append(Paragraph("Para alterar a configuração de um registrador de hardware sem modificar os outros bits que já estão configurados, usamos os operadores bitwise (<code>&amp;</code>, <code>|</code>, <code>^</code>, <code>~</code>, <code>&lt;&lt;</code>, <code>&gt;&gt;</code>):", style_body))

    code_bitwise = """// Exemplo pratico de escrita em registradores via Bitwise:
#define GPIOA_ODR  (*((volatile uint32_t*) 0x4001080C))

// 1. SETAR (Ligar) o bit 5 (PA5 = HIGH) mantendo os outros intactos
GPIOA_ODR |= (1U << 5);

// 2. CLEAR (Desligar) o bit 5 (PA5 = LOW)
GPIOA_ODR &= ~(1U << 5);

// 3. TOGGLE (Inverter o estado) do bit 5
GPIOA_ODR ^= (1U << 5);

// 4. MASK (Testar se o pino PA5 esta em nivel alto)
if (GPIOA_ODR & (1U << 5)) {
    // Pino acionado!
}"""
    story.append(Paragraph(code_bitwise.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code))

    story.append(Paragraph("3.4 Estruturas (<code>struct</code>), Unióes (<code>union</code>) e Enumerações (<code>enum</code>)", style_h2))
    story.append(Paragraph("• <b>Estruturas (<code>struct</code>):</b> Permitem criar abstrações completas de periféricos. A biblioteca ST HAL, por exemplo, mapeia o bloco de registradores do GPIO criando uma <code>struct</code> cujos membros correspondem exatamente ao deslocamento (<i>offset</i>) dos registradores na memória.<br/>• <b>Unióes (<code>union</code>):</b> Fazem com que diferentes membros compartilhem a mesma posição física de memória. São muito úteis para fatiar um número de 32 bits (<code>uint32_t</code>) em 4 bytes individuais (<code>uint8_t</code>) na hora de enviar dados pela porta serial ou USB, sem precisar fazer deslocamentos de bit manuais.<br/>• <b>Enumerações (<code>enum</code>):</b> Essenciais para criar Máquinas de Estados Finitos (<i>Finite State Machines</i> — FSM). Deixam o código do firmware muito mais legível para controlar os estados do sistema (ex.: <code>enum State {IDLE, DEBOUNCING, SEND_USB};</code>).", style_body))

    story.append(Paragraph("3.5 Ponteiros e Mapeamento de Memória (MMIO)", style_h2))
    story.append(Paragraph("Em C para sistemas embarcados, um ponteiro nada mais é do que a ferramenta usada para acessar o hardware. O mapa de memória do ARM Cortex-M3 associa cada periférico a um endereço base. Convertendo um valor hexadecimal de endereço para um ponteiro (<code>volatile uint32_t*</code>) e fazendo a desreferenciação (<code>*</code>), conseguimos ler e escrever no pino físico da placa em tempo real.", style_body))
    story.append(Paragraph("Além disso, os <b>ponteiros para função</b> são amplamente utilizados para implementar a tabela de vetores de interrupção (que aponta para o endereço inicial da rotina ISR que deve ser executada quando chega um sinal externo) e para configurar callbacks dinâmicos na biblioteca HAL (como o <code>HAL_TIM_PeriodElapsedCallback()</code>).", style_body))

    story.append(Paragraph("3.6 Macros e Pré-processador", style_h2))
    story.append(Paragraph("O uso de macros (<code>#define</code>) traz maior abstração e legibilidade ao firmware, permitindo renomear pinos de hardware (ex.: <code>#define LED_PIN GPIO_PIN_13</code>) e criar travas contra inclusão múltipla de cabeçalhos (<i>Include Guards</i>: <code>#ifndef _MAIN_H ... #endif</code>).", style_body))

    # 4. CONCLUSÃO
    story.append(Paragraph("4. Conclusão", style_h1))
    concl_text = """
    O estudo detalhado das videoaulas de <i>Embedded C</i> permitiu compreender com clareza as diferenças práticas entre desenvolver software de aplicação para PC e firmware para microcontroladores. A programação em sistemas embarcados exige uma postura muito mais rigorosa em relação ao uso de memória, controle de tempo e manipulação de registradores a nível de bits. Dominar o uso de tipos de tamanho fixo (<code>stdint.h</code>), o qualificador <code>volatile</code>, a manipulação bitwise e o mapeamento de memória por ponteiros e estruturas é indispensável para construir sistemas embarcados robustos, previsíveis e eficientes para o mercado de engenharia.
    """
    story.append(Paragraph(concl_text, style_body))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated Activity PDF: {pdf_filename}")

if __name__ == '__main__':
    pdf_out1 = os.path.join(os.path.dirname(__file__), 'Vicenzo_Olivalves_Atividade_Embedded_C.pdf')
    pdf_out2 = r'C:\Users\vicen\Downloads\Vicenzo_Olivalves_Atividade_Embedded_C.pdf'
    build_pdf_activity(pdf_out1)
    build_pdf_activity(pdf_out2)
