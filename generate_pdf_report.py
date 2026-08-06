# -*- coding: utf-8 -*-
"""
==============================================================================
 GERADOR DO RELATÓRIO TÉCNICO OFICIAL STREAM DECK UFU/FEELT (PDF)
==============================================================================
 Renderiza o documento PDF completo integrando todas as figuras do projeto
 (Fotos do Hardware, Montagem, KiCad PCB Face Simples B.Cu, STM32CubeMX,
 Interrupção de Timer TIM2 e tabelas de custos).
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable
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
            return  # Skip cover page

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#232679"))
        self.drawString(54, 800, "FEELT/UFU — RELATÓRIO TÉCNICO E MEMORIAL DESCRITIVO STREAM DECK")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))
        self.drawRightString(541, 800, "Sistemas Embarcados I")

        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(54, 792, 541, 792)

        # Footer
        self.line(54, 45, 541, 45)
        self.setFont("Helvetica", 9)
        self.drawString(54, 32, "Universidade Federal de Uberlândia — Faculdade de Engenharia Elétrica")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(541, 32, page_str)
        self.restoreState()

def build_pdf_report(pdf_filename):
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
        fontSize=10.5,
        leading=14,
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
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_text,
        alignment=4,
        spaceAfter=6
    )

    style_caption = ParagraphStyle(
        'Caption_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=10
    )

    style_code = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f8fafc"),
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=8
    )

    story = []

    # CAPA
    story.append(Spacer(1, 10))
    logo_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'ufu_logo.png')
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=70, height=70))
        story.append(Spacer(1, 15))

    story.append(Paragraph("UNIVERSIDADE FEDERAL DE UBERLÂNDIA", ParagraphStyle('UFU', fontName='Helvetica-Bold', fontSize=13, alignment=1)))
    story.append(Paragraph("FACULDADE DE ENGENHARIA ELÉTRICA — FEELT", ParagraphStyle('FEELT', fontName='Helvetica-Bold', fontSize=10, alignment=1)))
    story.append(Paragraph("DISCIPLINA DE SISTEMAS EMBARCADOS I", ParagraphStyle('DISC', fontName='Helvetica', fontSize=9, alignment=1)))
    story.append(Spacer(1, 45))

    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=15))
    story.append(Paragraph("RELATÓRIO TÉCNICO E MEMORIAL DESCRITIVO", style_cover_title))
    story.append(Paragraph("PROJETO STREAM DECK EMBARCADO COM VARREDURA POR INTERRUPÇÃO DE TIMER, PCB FACE SIMPLES E NATIVA USB HID", style_cover_sub))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=45))

    team_data = [
        [
            Paragraph("<b>Discentes / Integrantes:</b><br/>• Gustavo Martins Ribeiro Moura — 12111ETE002<br/>• Matheus Henrique Gonçalves — 12311ECP021<br/>• Vicenzo De Marco Olivalves — 12421ECP006", ParagraphStyle('TLeft', fontName='Helvetica', fontSize=9.5, leading=14)),
            Paragraph("<b>Docente Responsável:</b><br/>Prof. Jeovane Reges<br/><br/><b>Curso:</b><br/>Engenharia de Computação & Engenharia Eletrônica", ParagraphStyle('TRight', fontName='Helvetica', fontSize=9.5, leading=14))
        ]
    ]
    t_team = Table(team_data, colWidths=[240, 240])
    t_team.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 50))
    story.append(Paragraph("Uberlândia — MG<br/>30 de julho de 2026", ParagraphStyle('Date', fontName='Helvetica', fontSize=9, alignment=1)))
    story.append(PageBreak())

    # RESUMO
    story.append(Paragraph("Resumo", style_h1))
    resumo_text = """
    Este relatório apresenta o desenvolvimento, implementação e validação de um periférico de entrada dedicado (<b>Stream Deck / Macro Pad</b>) baseado no microcontrolador ARM Cortex-M3 (STM32F103C8T6 - Blue Pill). O dispositivo é composto por uma matriz 3x3 de teclas mecânicas acopladas a diodos anti-ghosting 1N4148, operando nativamente como protocolo USB Custom HID (<i>Human Interface Device</i>). O relatório especifica a compatibilidade mecânica dos switches (utilizando o padrão mecânico Cherry MX / Outemu Blue de 3 pinos adquirido no mercado nacional). Em estrito atendimento às recomendações da banca, a arquitetura do firmware foi totalmente reformulada para operar <b>100% sob Interrupção de Hardware por Timer (TIM2 a 100 Hz / 10 ms)</b> com filtro de debouncing por máquina de estados, eliminando o uso ineficiente de <i>polling</i> no loop principal. Adicionalmente, a placa de circuito impresso (PCB) foi projetada no KiCad em <b>camada única (Face Simples B.Cu)</b> com trilhas engrossadas de 0,8 mm a 1,2 mm, viabilizando a corrosão artesanal manual com Percloreto de Ferro.
    """
    story.append(Paragraph(resumo_text, style_body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Sumário Executivo", style_h1))
    sumario_data = [
        ["Seção", "Descrição do Conteúdo"],
        ["1. Introdução", "Contextualização e aplicação prática do Stream Deck."],
        ["2. Objetivos", "Objetivo geral e objetivos específicos do projeto."],
        ["3. Fundamentação Teórica", "Sistemas embarcados, matriz 3x3, diodos 1N4148 e switches MX Blue."],
        ["4. Materiais e Metodologia", "Lista detalhada de materiais e processo de montagem."],
        ["5. Resultados e Discussão", "KiCad Face Simples B.Cu (0,8-1,2mm), STM32CubeMX, TIM2 ISR e Código C."],
        ["6. Análise de Custos", "Tabela orçamentária dos materiais (Total: R$ 128,73)."],
        ["7. Conclusão", "Síntese dos resultados e conformidade aos requisitos."]
    ]
    t_sumario = Table(sumario_data, colWidths=[140, 340])
    t_sumario.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(t_sumario)
    story.append(Spacer(1, 15))

    # 1. INTRODUÇÃO
    story.append(Paragraph("1. Introdução", style_h1))
    story.append(Paragraph("Os sistemas embarcados estão presentes em diversas aplicações tecnológicas, desempenhando funções específicas por meio da integração entre hardware e software. Esses sistemas são amplamente utilizados em dispositivos eletrônicos que exigem processamento dedicado, baixo consumo de energia e interação eficiente com o usuário, tornando-se fundamentais em áreas como automação, controle e interfaces inteligentes.", style_body))
    story.append(Paragraph("Neste contexto, o desenvolvimento de um Stream Deck representa uma aplicação prática dos conceitos estudados na disciplina de Sistemas Embarcados I da UFU/FEELT. O dispositivo consiste em um controlador com teclas programáveis, capaz de executar comandos previamente configurados, como abertura de programas, envio de atalhos de teclado (F13 a F21), controle de aplicações e automação de tarefas. Essa tecnologia é amplamente empregada por criadores de conteúdo, profissionais de transmissão ao vivo, designers e programadores.", style_body))

    # 2. OBJETIVOS
    story.append(Paragraph("2. Objetivos", style_h1))
    story.append(Paragraph("2.1 Objetivo Geral", style_h2))
    story.append(Paragraph("Desenvolver um Stream Deck utilizando conceitos de sistemas embarcados, integrando hardware e software para criar um dispositivo capaz de executar comandos e automatizar tarefas por meio de teclas programáveis.", style_body))

    story.append(Paragraph("2.2 Objetivos Específicos", style_h2))
    story.append(Paragraph("• Implementar a programação do microcontrolador responsável pelo gerenciamento das entradas por meio de <b>Interrupção de Timer de Hardware (TIM2)</b>, eliminando o polling.<br/>• Especificar a compatibilidade mecânica dos switches (utilizando o padrão mecânico Cherry MX / Outemu Blue de 3 pinos adquirido no mercado nacional com encaixe 14mm x 14mm).<br/>• Desenvolver a PCB no KiCad em <b>Face Simples (Single Layer B.Cu)</b> com trilhas engrossadas (0,8 mm a 1,2 mm) para permitir a fabricação manual por corrosão em Percloreto de Ferro.<br/>• Integrar a comunicação USB Custom HID bidirecional para troca de relatórios IN e OUT com a aplicação em Python 3.<br/>• Consolidar a montagem física com carcaça impressa em 3D, insertos roscados M3 e parafusos M3x8mm.", style_body))

    # 3. FUNDAMENTAÇÃO TEÓRICA
    story.append(Paragraph("3. Fundamentação Teórica", style_h1))
    story.append(Paragraph("Os sistemas embarcados são sistemas computacionais dedicados ao desempenho de funções específicas, integrando hardware e software em um único dispositivo. Diferentemente dos computadores de uso geral, esses sistemas são projetados para executar tarefas determinadas com alta eficiência, confiabilidade e baixo consumo de recursos.", style_body))
    story.append(Paragraph("O funcionamento do Stream Deck baseia-se na leitura do estado das teclas por um microcontrolador, que interpreta cada acionamento e envia o comando correspondente ao computador. Para garantir o correto funcionamento do teclado, utiliza-se uma matriz de teclas associada a diodos 1N4148, evitando o fenômeno conhecido como <i>ghosting</i>, que pode provocar o reconhecimento incorreto de múltiplas teclas pressionadas simultaneamente.", style_body))
    story.append(Paragraph("Os switches mecânicos (especificados no padrão Cherry MX / Outemu Blue com encaixe 14 mm x 14 mm e força de atuação de 60g) proporcionam maior precisão e durabilidade em relação aos botões convencionais. A estrutura física do dispositivo é produzida por manufatura aditiva (impressão 3D), permitindo a fabricação de uma carcaça personalizada, de baixo custo e adequada às dimensões do circuito eletrônico.", style_body))

    # 4. MATERIAIS E METODOLOGIA
    story.append(Paragraph("4. Materiais e Metodologia", style_h1))
    story.append(Paragraph("O desenvolvimento do projeto foi dividido em etapas que envolveram o planejamento do dispositivo, a montagem do circuito eletrônico no KiCad, a programação do microcontrolador STM32, a fabricação da estrutura mecânica em impressão 3D e a realização dos testes de funcionamento.", style_body))
    story.append(Paragraph("<b>Lista de Materiais Utilizados:</b><br/>• 9 switches mecânicos genéricos (Padrão Cherry MX / Outemu Blue de 3 pinos);<br/>• 9 diodos de sinal 1N4148;<br/>• Microcontrolador STM32F103C8T6 (Blue Pill - ARM Cortex-M3 @ 72 MHz);<br/>• Fios para ligação elétrica;<br/>• 4 insertos roscados M3 em latão;<br/>• 4 parafusos M3 de 8 mm;<br/>• Fita isolante espumada;<br/>• Carcaça produzida em impressão 3D.", style_body))

    # 5. RESULTADOS E DISCUSSÃO
    story.append(Paragraph("5. Resultados e Discussão", style_h1))

    story.append(Paragraph("5.1 Projeto Eletrônico no KiCad (PCB Face Simples Manual)", style_h2))
    story.append(Paragraph("A primeira etapa do desenvolvimento consistiu na elaboração do esquema elétrico e do layout da placa de circuito impresso utilizando o software KiCad. Atendendo à solicitação do professor, o layout da placa foi desenvolvido exclusivamente na <b>camada inferior de cobre (<code>B.Cu</code> - Face Simples)</b>, facilitando o processo de confecção artesanal por transferência térmica. As trilhas foram engrossadas para larguras entre <b>0,8 mm (31,5 mils)</b> e <b>1,2 mm (47,2 mils)</b> com espaçamento de segurança de <b>0,5 mm</b>, eliminando riscos de rompimento ou curto-circuito na corrosão por Percloreto de Ferro.", style_body))

    # Embed Images if present
    hw_img_path = os.path.join(os.path.dirname(__file__), 'streamdeck_hardware.png')
    assembly_img_path = os.path.join(os.path.dirname(__file__), 'streamdeck_assembly.jpg')

    if os.path.exists(hw_img_path):
        story.append(Image(hw_img_path, width=340, height=255))
        story.append(Paragraph("Figura 1 — Protótipo físico finalizado do Stream Deck em carcaça impressa 3D.", style_caption))

    if os.path.exists(assembly_img_path):
        story.append(Image(assembly_img_path, width=340, height=255))
        story.append(Paragraph("Figura 2 — Processo de soldagem e montagem física dos switches mecânicos e diodos 1N4148.", style_caption))

    story.append(Paragraph("5.2 Configuração e Programação no STM32CubeMX", style_h2))
    story.append(Paragraph("As portas GPIO foram configuradas da seguinte forma no STM32CubeMX:<br/>• <b>Linhas (LINE_1 a LINE_3):</b> Pinos PA1, PA2, PA3 configurados como <code>GPIO_MODE_OUTPUT_OD</code> (Open Drain).<br/>• <b>Colunas (COL_1 a COL_3):</b> Pinos PA4, PA5, PA6 configurados como <code>GPIO_MODE_INPUT</code> com <code>GPIO_PULLUP</code> interno.<br/>• <b>Comunicação USB HID:</b> Pinos PA11 (USB_DM) e PA12 (USB_DP) na classe Custom HID.<br/>• <b>Gravador SWD:</b> Pinos PA13 (SYS_JTMS-SWDIO) e PA14 (SYS_JTCK-SWCLK).", style_body))
    story.append(Paragraph("A árvore de clock do sistema foi configurada utilizando o oscilador cristal externo (HSE) de 8 MHz com multiplicador PLL x9, resultando em uma frequência principal de <b>72 MHz (SYSCLK)</b>. Para o correto funcionamento do periférico USB Full-Speed (12 Mbps), aplicou-se o divisor dedicado USB de <b>/1.5</b>, gerando exatos <b>48 MHz (USBCLK)</b>.", style_body))

    story.append(Paragraph("5.3 Varredura por Interrupção de Timer (TIM2)", style_h2))
    story.append(Paragraph("Para atender integralmente à exigência de eliminar o polling no <code>while(1)</code>, o timer de hardware <b>TIM2</b> foi configurado com prescaler 7199 e período 99, gerando interrupções periódicas de hardware a cada <b>10 ms (100 Hz)</b>. A função <code>HAL_TIM_PeriodElapsedCallback()</code> executa a varredura e o debouncing de 40 ms. O loop principal no <code>main()</code> permanece 100% ocioso executando a instrução de baixo consumo <code>__WFI()</code>.", style_body))

    code_snippet = """// Trecho Principal do Firmware por Interrupcao (main.c)
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM2) {
        int current_key = scanMatrix_ISR(); // Varre matriz 3x3
        if (current_key != last_raw_key) {
            sample_ticks = HAL_GetTick();
            last_raw_key = current_key;
        }
        if ((HAL_GetTick() - sample_ticks) >= 40) { // Debounce 40ms
            if (current_key != stable_valid_key) {
                stable_valid_key = current_key;
                uint8_t hid_report[8] = {0};
                if (stable_valid_key != -1) {
                    hid_report[2] = 0x68 + stable_valid_key; // F13..F21
                }
                USBD_CUSTOM_HID_SendReport(&hUsbDeviceFS, hid_report, 8);
            }
        }
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USB_DEVICE_Init();
    MX_TIM2_Init();

    HAL_TIM_Base_Start_IT(&htim2); // Ativa Interrupcao TIM2 (100Hz)

    while (1) {
        __WFI(); // CPU em Idle (Wait For Interrupt)
    }
}"""
    story.append(Paragraph(code_snippet.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code))

    story.append(Paragraph("5.4 Montagem Física do Protótipo", style_h2))
    story.append(Paragraph("Após a definição do circuito eletrônico e da programação do microcontrolador, foi realizada a montagem física do Stream Deck. Inicialmente, foi confeccionada uma carcaça por meio de impressão 3D, projetada para acomodar os switches mecânicos, o microcontrolador Blue Pill e os demais componentes do sistema. Em seguida, os nove switches mecânicos foram instalados na carcaça e interligados aos diodos 1N4148 por meio de soldagem.", style_body))

    # 6. CUSTOS
    story.append(Paragraph("6. Análise de Custos", style_h1))
    custo_data = [
        ["Componente / Insumo", "Qtd", "Valor Unit. (R$)", "Valor Total (R$)"],
        ["Switch Mecânico Genérico MX Blue (Mercado Livre)", "9", "2,84", "25,56"],
        ["Diodo de Sinal 1N4148", "9", "0,20", "1,80"],
        ["Microcontrolador STM32F103C8T6 (Blue Pill)", "1", "40,00", "40,00"],
        ["Fios de Ligação", "1,5m", "1,80 (1m)", "2,70"],
        ["Inserto Roscado M3 em Latão", "4", "0,65", "2,67"],
        ["Fita Isolante Espumada", "1", "4,00", "4,00"],
        ["Parafuso M3 x 8mm", "4", "0,50", "2,00"],
        ["Carcaça produzida em impressão 3D", "1", "50,00", "50,00"],
        ["CUSTO TOTAL DO PROTÓTIPO", "", "", "R$ 128,73"]
    ]
    t_custo = Table(custo_data, colWidths=[180, 40, 130, 130])
    t_custo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#f1f5f9")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    story.append(t_custo)
    story.append(Spacer(1, 15))

    # 7. CONCLUSÃO
    story.append(Paragraph("7. Conclusão", style_h1))
    conclusao_text = """
    O desenvolvimento do Stream Deck customizado demonstrou-se totalmente viável na integração entre a arquitetura de hardware e o projeto mecânico. A utilização do microcontrolador STM32F103C8T6 (Blue Pill), configurado via STM32CubeMX e programado com <b>Interrupção de Timer de Hardware (TIM2 a 100 Hz)</b> para operar como um dispositivo USB HID com clock ajustado em 48 MHz, assegurou a comunicação nativa e o disparo imediato de atalhos e macros no computador sem o uso de <i>polling</i>. A organização da leitura dos botões em uma matriz 3x3 com diodos anti-ghosting 1N4148 otimizou a alocação dos pinos do chip. A PCB projetada em <b>face simples (<code>B.Cu</code>) com trilhas reforçadas de 0,8 mm a 1,2 mm</b> viabilizou a confecção artesanal. Dessa forma, o projeto valida a aplicação prática de sistemas embarcados e prototipagem física na criação de um periférico funcional, preciso e sob medida.
    """
    story.append(Paragraph(conclusao_text, style_body))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF report: {pdf_filename}")

if __name__ == '__main__':
    pdf_out = os.path.join(os.path.dirname(__file__), 'RELATORIO_STREAMDECK_UFU.pdf')
    build_pdf_report(pdf_out)
