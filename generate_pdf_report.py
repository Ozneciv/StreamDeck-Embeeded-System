# -*- coding: utf-8 -*-
"""
==============================================================================
 GERADOR DO RELATÓRIO TÉCNICO OFICIAL STREAM DECK UFU/FEELT (PDF)
==============================================================================
 Converte e gera o documento em PDF completo atendendo a todas as observações
 e críticas do professor (Interrupções por Hardware, Timer TIM2, PCB Face Simples
 com trilhas grossas, comunicação bidirecional e código C documentado).
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable, KeepTogether
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

    # Colors
    c_primary = colors.HexColor("#232679")
    c_dark = colors.HexColor("#0f143c")
    c_accent = colors.HexColor("#ffab00")
    c_text = colors.HexColor("#1f2937")

    # Custom Styles
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        alignment=1, # Center
        spaceAfter=15
    )

    style_cover_sub = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_dark,
        alignment=1,
        spaceAfter=25
    )

    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_dark,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_text,
        alignment=4, # Justified
        spaceAfter=6
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

    # =========================================================================
    # CAPA
    # =========================================================================
    story.append(Spacer(1, 10))
    logo_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'ufu_logo.png')
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=70, height=70))
        story.append(Spacer(1, 10))

    story.append(Paragraph("UNIVERSIDADE FEDERAL DE UBERLÂNDIA", ParagraphStyle('UFU', fontName='Helvetica-Bold', fontSize=12, alignment=1)))
    story.append(Paragraph("FACULDADE DE ENGENHARIA ELÉTRICA — FEELT", ParagraphStyle('FEELT', fontName='Helvetica-Bold', fontSize=10, alignment=1)))
    story.append(Paragraph("DISCIPLINA DE SISTEMAS EMBARCADOS I (PROF. JEOVANE REGES)", ParagraphStyle('DISC', fontName='Helvetica', fontSize=9, alignment=1)))
    story.append(Spacer(1, 40))

    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=0, spaceAfter=15))
    story.append(Paragraph("RELATÓRIO TÉCNICO \& MEMORIAL DESCRITIVO", style_cover_title))
    story.append(Paragraph("STREAM DECK EMBARCADO COM MATRIZ 3x3, INTERRUPÇÃO POR TIMER DE HARDWARE E PCB FACE SIMPLES", style_cover_sub))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=0, spaceAfter=40))

    team_text = """
    <b>Discentes / Integrantes:</b><br/>
    • Bruna de Jesus Silva — 12021ETE007<br/>
    • Gustavo Martins Ribeiro Moura — 12111ETE002<br/>
    • Matheus Henrique Gonçalves — 12311ECP021<br/>
    • Vicenzo De Marco Olivalves — 12421ECP006
    """
    story.append(Paragraph(team_text, ParagraphStyle('Team', fontName='Helvetica', fontSize=10, leading=15)))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Uberlândia — MG<br/>30 de julho de 2026", ParagraphStyle('Date', fontName='Helvetica', fontSize=9, alignment=1)))
    story.append(PageBreak())

    # =========================================================================
    # RESUMO & SUMÁRIO
    # =========================================================================
    story.append(Paragraph("Resumo", style_h1))
    resumo_text = """
    Este relatório apresenta a reestruturação e implementação completa do projeto de um periférico de entrada dedicado (<b>Stream Deck / Macro Pad</b>) baseado no microcontrolador ARM Cortex-M3 (STM32F103C8T6 - Blue Pill). O sistema possui 9 teclas mecânicas (3x3) associadas a diodos anti-ghosting 1N4148, comunicando-se nativamente com o computador via protocolo USB Custom HID (<i>Human Interface Device</i>). Atendendo integralmente às críticas do professor, a arquitetura de firmware foi reformulada para operar <b>100% sob Interrupção de Hardware por Timer (TIM2 a 100 Hz)</b>, eliminando completamente a leitura por polling no loop principal. Adicionalmente, a placa de circuito impresso (PCB) foi projetada no KiCad em <b>camada única (Face Simples B.Cu)</b> com trilhas reforçadas de <b>0,8 mm a 1,2 mm</b> e distância de segurança de 0,5 mm, viabilizando a fabricação artesanal e corrosão manual com Percloreto de Ferro. O protótipo conta com comunicação bidirecional com o PC e interface de acompanhamento em Python 3.
    """
    story.append(Paragraph(resumo_text, style_body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Sumário Executivo do Documento", style_h1))
    sumario_data = [
        ["Seção", "Descrição do Conteúdo"],
        ["1. Introdução e Objetivos", "Contextualização, escopo e metas específicas do projeto."],
        ["2. Memorial Descritivo e Limitações", "Justificativas de hardware, características e limitações do sistema."],
        ["3. Comunicação Bidirecional USB HID", "Descritor USB HID (IN/OUT Reports) e sincronização com Python."],
        ["4. PCB Face Simples para Confecção Manual", "Roteamento B.Cu, trilhas reforçadas (0,8-1,2mm) e isolamento."],
        ["5. Firmware por Interrupção de Timer (TIM2)", "Varredura 100Hz ISR, filtro debouncing não-bloqueante e código C."],
        ["6. Análise de Custos e Viabilidade", "Planilha orçamentária detalhada dos insumos."],
        ["7. Conclusão", "Síntese dos resultados obtidos."]
    ]
    t_sumario = Table(sumario_data, colWidths=[130, 350])
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

    # =========================================================================
    # 1. INTRODUÇÃO E OBJETIVOS
    # =========================================================================
    story.append(Paragraph("1. Introdução e Objetivos", style_h1))
    story.append(Paragraph("O desenvolvimento de periféricos computacionais dedicados é um dos pilares práticos da engenharia de Sistemas Embarcados. Este projeto aborda a criação de um <i>Stream Deck</i> de 9 teclas mecânicas controlado pela placa STM32F103C8T6 (ARM Cortex-M3), unindo o projeto de hardware, confecção de placa de circuito impresso (PCB) artesanal e desenvolvimento de firmware de baixo nível.", style_body))

    story.append(Paragraph("1.1 Objetivo Geral", style_h2))
    story.append(Paragraph("Desenvolver um Stream Deck embarcado integrado por hardware e software, apresentando varredura por Interrupção de Hardware de Timer (TIM2 a 100 Hz), comunicação USB Custom HID bidirecional, e PCB de face simples pronta para corrosão manual.", style_body))

    story.append(Paragraph("1.2 Objetivos Específicos", style_h2))
    story.append(Paragraph("• <b>Eliminação de Polling:</b> Substituir o loop principal bloqueante por interrupção periódica de hardware (TIM2 ISR a 100 Hz / 10 ms).<br/>• <b>Debouncing por Máquina de Estados:</b> Implementar a filtragem temporal na ISR sem congelar a CPU.<br/>• <b>PCB Face Simples Manual:</b> Roteamento na camada inferior (<code>B.Cu</code>) com trilhas grossas (0,8 mm a 1,2 mm) para transferência térmica.<br/>• <b>Comunicação Bidirecional:</b> Envio de relatórios IN de 8 Bytes (F13..F21) e recepção de relatórios OUT de estado.", style_body))

    # =========================================================================
    # 2. MEMORIAL DESCRITIVO E LIMITAÇÕES
    # =========================================================================
    story.append(Paragraph("2. Memorial Descritivo, Justificativas e Limitações", style_h1))
    story.append(Paragraph("<b>Justificativa do Microcontrolador:</b> O STM32F103C8T6 (72 MHz, 32-bit ARM Cortex-M3) possui periférico USB 2.0 Full-Speed integrado e timers de 16 bits. Sua capacidade de chaveamento Open-Drain nas GPIOs (<code>PA1..PA3</code>) é essencial para isolar as linhas da matriz sem provocar curtos-circuitos durante pressionamentos simultâneos.", style_body))

    story.append(Paragraph("<b>Proteção Anti-Ghosting:</b> Cada switch mecânico possui um diodo 1N4148 em série, bloqueando correntes reversas entre colunas e impedindo o efeito de <i>ghosting</i>.", style_body))

    story.append(Paragraph("Matriz de Características e Limitações Técnicas", style_h2))
    limit_data = [
        ["Parâmetro / Característica", "Especificação", "Justificativa de Engenharia"],
        ["Frequência do Núcleo", "72 MHz (SYSCLK)", "Cristal HSE 8MHz com PLL x9."],
        ["Clock do Periférico USB", "48 MHz (USBCLK)", "Prescaler PLL /1.5 obrigatório do USB Full-Speed."],
        ["Varredura da Matriz", "Interrupção Timer TIM2", "Amostragem periódica a cada 10ms (100 Hz)."],
        ["Debouncing Temporal", "40 ms por ISR", "Filtro temporal estabilizado sem atrasar a rotina USB."],
        ["Roteamento PCB", "Face Simples (B.Cu)", "Facilita confecção manual por percloreto de ferro."],
        ["Espessura das Trilhas", "0,8 mm a 1,2 mm", "Evita rompimento de cobre durante a corrosão artesanal."]
    ]
    t_limit = Table(limit_data, colWidths=[120, 140, 220])
    t_limit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(t_limit)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 3. COMUNICAÇÃO BIDIRECIONAL
    # =========================================================================
    story.append(Paragraph("3. Comunicação Bidirecional USB Custom HID", style_h1))
    story.append(Paragraph("O dispositivo atua como um controle de interface humana (Custom HID), estabelecendo comunicação bidirecional com o PC:", style_body))
    story.append(Paragraph("1. <b>Canal IN (STM32 -> PC):</b> Envia relatórios de 8 Bytes contendo o código estendido da tecla (F13 = <code>0x68</code> até F21 = <code>0x70</code>).<br/>2. <b>Canal OUT (PC -> STM32):</b> O servidor Python (<code>app.py</code>) envia pacotes de retorno indicando o status do sistema (microfone mutado, cena do OBS ativa ou alarme), acionando respostas visuais no hardware.", style_body))

    # =========================================================================
    # 4. PCB FACE SIMPLES PARA CONFECÇÃO MANUAL
    # =========================================================================
    story.append(Paragraph("4. PCB Face Simples para Confecção Manual", style_h1))
    story.append(Paragraph("Atendendo à exigência de confecção física manual da placa pelo aluno:", style_body))
    story.append(Paragraph("• <b>Camada Única (B.Cu):</b> Todo o roteamento foi alocado exclusivamente na camada de cobre inferior.<br/>• <b>Trilhas Reforçadas:</b> As trilhas possuem largura de <b>0,8 mm (31.5 mils)</b> para sinais e <b>1,2 mm (47.2 mils)</b> para alimentação.<br/>• <b>Pads Ampliados (Hand Soldering):</b> Ilhas de solda com diâmetro expandido para facilitar a perfuração com broca de 0,8mm e soldagem com ferro de solda comum.", style_body))

    # =========================================================================
    # 5. FIRMWARE POR INTERRUPÇÃO DE TIMER (TIM2)
    # =========================================================================
    story.append(Paragraph("5. Firmware STM32 Baseado em Interrupção por Hardware", style_h1))
    story.append(Paragraph("O programa principal foi completamente refatorado para eliminar o <i>polling</i> no loop <code>while(1)</code>. A varredura da matriz 3x3 e o filtro de debouncing são executados dentro da rotina de interrupção <code>HAL_TIM_PeriodElapsedCallback()</code> acionada pelo Timer TIM2 a cada 10ms (100 Hz).", style_body))

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
        __WFI(); // CPU entra em Wait For Interrupt (Zero Polling)
    }
}"""
    story.append(Paragraph(code_snippet.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code))

    # =========================================================================
    # 6. ANÁLISE DE CUSTOS
    # =========================================================================
    story.append(Paragraph("6. Análise de Custos do Protótipo", style_h1))
    custo_data = [
        ["Componente / Insumo", "Qtd", "Valor Unit. (R$)", "Valor Total (R$)"],
        ["Switch Mecânico Cherry MX Compatible", "9", "2,84", "25,56"],
        ["Diodo de Sinal 1N4148", "9", "0,20", "1,80"],
        ["Microcontrolador STM32F103C8T6 (Blue Pill)", "1", "40,00", "40,00"],
        ["Fios e Condutores de Conexão", "1,5m", "1,80", "2,70"],
        ["Insertos Roscados M3 em Latão", "4", "0,65", "2,67"],
        ["Fita Isolante Espumada", "1", "4,00", "4,00"],
        ["Parafusos M3 x 8mm", "4", "0,50", "2,00"],
        ["Carcaça Personalizada em Impressão 3D", "1", "50,00", "50,00"],
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

    # =========================================================================
    # 7. CONCLUSÃO
    # =========================================================================
    story.append(Paragraph("7. Conclusão", style_h1))
    conclusao_text = """
    A reestruturação completa do projeto atendeu rigorosamente a todas as diretrizes e críticas da banca examinadora. A eliminação do <i>polling</i> em prol de uma arquitetura orientada a <b>Interrupção por Hardware de Timer (TIM2 a 100 Hz)</b> reduziu a carga da CPU e garantiu temporização determinística. A PCB foi adaptada para <b>face simples (Single-Layer B.Cu) com trilhas espessas de 0,8 mm a 1,2 mm</b>, viabilizando a produção manual em bancada. O trabalho consolida de forma robusta e profissional todos os requisitos acadêmicos da disciplina de Sistemas Embarcados I da FEELT/UFU.
    """
    story.append(Paragraph(conclusao_text, style_body))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF report: {pdf_filename}")

if __name__ == '__main__':
    pdf_out = os.path.join(os.path.dirname(__file__), 'RELATORIO_STREAMDECK_UFU.pdf')
    build_pdf_report(pdf_out)
