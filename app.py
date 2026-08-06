# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import ttk, messagebox
import time
import math
import random
try:
    import winsound
except ImportError:
    winsound = None

# Mapeamento dos Botões F13 a F21 (Scancodes 0x68 a 0x70)
DECK_BUTTONS = [
    {"id": 0, "key": "F13", "num": "1", "hex": "0x68", "label": "Soundboard SFX", "icon": "🔊", "row_pin": "PA1", "col_pin": "PA4"},
    {"id": 1, "key": "F14", "num": "2", "hex": "0x69", "label": "Mudo / On-Air", "icon": "🎙️", "row_pin": "PA1", "col_pin": "PA5"},
    {"id": 2, "key": "F15", "num": "3", "hex": "0x6A", "label": "Alternar Cena", "icon": "🎬", "row_pin": "PA1", "col_pin": "PA6"},
    {"id": 3, "key": "F16", "num": "4", "hex": "0x6B", "label": "Cronômetro", "icon": "⏱️", "row_pin": "PA2", "col_pin": "PA4"},
    {"id": 4, "key": "F17", "num": "5", "hex": "0x6C", "label": "Alerta Sala", "icon": "🔔", "row_pin": "PA2", "col_pin": "PA5"},
    {"id": 5, "key": "F18", "num": "6", "hex": "0x6D", "label": "Efeitos LED", "icon": "💡", "row_pin": "PA2", "col_pin": "PA6"},
    {"id": 6, "key": "F19", "num": "7", "hex": "0x6E", "label": "Diagrama STM32", "icon": "⚡", "row_pin": "PA3", "col_pin": "PA4"},
    {"id": 7, "key": "F20", "num": "8", "hex": "0x6F", "label": "Meme Embarcados", "icon": "🤖", "row_pin": "PA3", "col_pin": "PA5"},
    {"id": 8, "key": "F21", "num": "9", "hex": "0x70", "label": "Celebração", "icon": "🎉", "row_pin": "PA3", "col_pin": "PA6"}
]

MEMES = [
    "\"Compilou sem warnings na primeira tentativa... Deve ter algo muito errado!\"",
    "\"Por que usar um botão comum se você pode configurar 32 registradores e uma matriz 3x3 no STM32?\"",
    "\"Ponteiros em C não são assustadores... até você esquecer de inicializar e tomar um HardFault Exception!\"",
    "\"Quando o debounce por código funciona perfeitamente de primeira: 🧙‍♂️ Mágica!\"",
    "\"STM32 BluePill: R$ 25,00. Orgulho de fazer um StreamDeck próprio: Não tem preço!\""
]

class StreamDeckPythonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stream Deck - Sistemas Embarcados - FEELT UFU")
        self.root.geometry("1024x680")
        self.root.configure(bg="#0a0c10")

        # Estado da Aplicação
        self.is_mic_muted = False
        self.timer_running = False
        self.timer_seconds = 0
        self.scene_index = 0
        self.meme_index = 0

        self.setup_ui()
        self.bind_keyboard_events()

    def setup_ui(self):
        # 1. Header Superior
        header = tk.Frame(self.root, bg="#12161f", height=70, highlightbackground="#232679", highlightthickness=1)
        header.pack(fill="x", side="top")

        title_label = tk.Label(
            header,
            text="Stream Deck - Sistemas Embarcados - FEELT UFU",
            font=("Helvetica", 14, "bold"),
            fg="#00f2fe",
            bg="#12161f"
        )
        title_label.pack(side="left", padx=20, pady=10)

        sub_label = tk.Label(
            header,
            text="Interface Nativa em Python 3 (Tkinter GUI)",
            font=("Consolas", 9, "bold"),
            fg="#ffab00",
            bg="#12161f"
        )
        sub_label.pack(side="right", padx=20, pady=10)

        # 2. Main Layout (Esquerda: Hardware/Integrantes | Direita: Palco/Telemetria)
        main_frame = tk.Frame(self.root, bg="#0a0c10")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Painel Esquerdo
        left_panel = tk.Frame(main_frame, bg="#181d28", width=420, highlightbackground="#232679", highlightthickness=1)
        left_panel.pack(side="left", fill="y", padx=(0, 10))

        # Título Matriz
        lbl_mat = tk.Label(left_panel, text=" Matriz de Teclas (3x3 - GPIO) ", font=("Helvetica", 11, "bold"), fg="#f0f4f8", bg="#181d28")
        lbl_mat.pack(anchor="w", padx=15, pady=(15, 5))

        # Matriz 3x3 de Botões
        grid_frame = tk.Frame(left_panel, bg="#181d28")
        grid_frame.pack(padx=15, pady=5)

        self.btn_widgets = []
        for btn_info in DECK_BUTTONS:
            idx = btn_info["id"]
            r, c = idx // 3, idx % 3
            btn_text = f"{btn_info['icon']}  #{idx+1}\n{btn_info['key']} ({btn_info['hex']})\n{btn_info['label']}"
            
            b = tk.Button(
                grid_frame,
                text=btn_text,
                font=("Helvetica", 8, "bold"),
                fg="#f0f4f8",
                bg="#1e2535",
                activebackground="#00f2fe",
                activeforeground="#000000",
                bd=2,
                relief="groove",
                width=14,
                height=4,
                command=lambda i=idx: self.trigger_action(i)
            )
            b.grid(row=r, column=c, padx=4, pady=4)
            self.btn_widgets.append(b)

        # Telemetria de Pinos
        telemetry_frame = tk.LabelFrame(left_panel, text=" Telemetria de Pinos (GPIO) ", font=("Helvetica", 9, "bold"), fg="#8a99ad", bg="#181d28", bd=1)
        telemetry_frame.pack(fill="x", padx=15, pady=10)

        self.lbl_pins_row = tk.Label(telemetry_frame, text="Linha Ativa: Nenhuma", font=("Consolas", 8, "bold"), fg="#ff0844", bg="#181d28")
        self.lbl_pins_row.pack(anchor="w", padx=10, pady=2)

        self.lbl_pins_col = tk.Label(telemetry_frame, text="Coluna Ativa: Nenhuma", font=("Consolas", 8, "bold"), fg="#00e676", bg="#181d28")
        self.lbl_pins_col.pack(anchor="w", padx=10, pady=2)

        self.lbl_hex_code = tk.Label(telemetry_frame, text="HID Report Byte 2: 0x00", font=("Consolas", 8), fg="#00f2fe", bg="#181d28")
        self.lbl_hex_code.pack(anchor="w", padx=10, pady=2)

        # Integrantes
        team_frame = tk.LabelFrame(left_panel, text=" Integrantes do Projeto (FEELT / UFU) ", font=("Helvetica", 9, "bold"), fg="#ffab00", bg="#181d28", bd=1)
        team_frame.pack(fill="x", padx=15, pady=(5, 15))

        members = [
            ("Vicenzo De Marco Olivalves", "12421ECP006"),
            ("Mateus Henrique Gonçalves", "12311ECP021"),
            ("Gustavo Martins", "12111ETE002"),
            ("Bruna Silva", "12021ETE007")
        ]
        for name, reg in members:
            row_f = tk.Frame(team_frame, bg="#181d28")
            row_f.pack(fill="x", padx=8, pady=2)
            tk.Label(row_f, text=name, font=("Helvetica", 8, "bold"), fg="#f0f4f8", bg="#181d28").pack(side="left")
            tk.Label(row_f, text=reg, font=("Consolas", 8), fg="#ffab00", bg="#181d28").pack(side="right")

        # Painel Direito (Palco da Apresentação)
        right_panel = tk.Frame(main_frame, bg="#181d28", highlightbackground="#232679", highlightthickness=1)
        right_panel.pack(side="right", fill="both", expand=True)

        lbl_stage_title = tk.Label(right_panel, text=" Palco de Simulação em Sala (Python Stage) ", font=("Helvetica", 11, "bold"), fg="#f0f4f8", bg="#181d28")
        lbl_stage_title.pack(anchor="w", padx=15, pady=15)

        # Stage Display Area
        self.stage_card = tk.Frame(right_panel, bg="#0a0c10", highlightbackground="#00f2fe", highlightthickness=1)
        self.stage_card.pack(fill="both", expand=True, padx=15, pady=5)

        self.stage_label_main = tk.Label(self.stage_card, text="🚀\nDemonstração Stream Deck STM32", font=("Helvetica", 18, "bold"), fg="#00f2fe", bg="#0a0c10")
        self.stage_label_main.pack(expand=True)

        self.stage_label_sub = tk.Label(self.stage_card, text="Pressione teclas F13..F21 ou aperte os botões da matriz para disparar ações em Python!", font=("Helvetica", 10), fg="#8a99ad", bg="#0a0c10")
        self.stage_label_sub.pack(pady=(0, 30))

        # Action Log Bar
        log_bar = tk.Frame(right_panel, bg="#0a0c10", height=40)
        log_bar.pack(fill="x", side="bottom", padx=15, pady=15)

        self.lbl_log = tk.Label(log_bar, text="[LOG PYTHON] Aguardando acionamento das teclas...", font=("Consolas", 9), fg="#00e676", bg="#0a0c10")
        self.lbl_log.pack(side="left", padx=10, pady=8)

    def bind_keyboard_events(self):
        for btn in DECK_BUTTONS:
            self.root.bind(f"<{btn['key']}>", lambda e, b_id=btn['id']: self.trigger_action(b_id))
            self.root.bind(btn['num'], lambda e, b_id=btn['id']: self.trigger_action(b_id))

    def trigger_action(self, btn_id):
        btn = DECK_BUTTONS[btn_id]
        
        # Visual feedback no botão
        widget = self.btn_widgets[btn_id]
        widget.config(bg="#00f2fe", fg="#000000")
        self.root.after(200, lambda: widget.config(bg="#1e2535", fg="#f0f4f8"))

        # Atualizar Telemetria
        self.lbl_pins_row.config(text=f"Linha Ativa: {btn['row_pin']} (GND Out)")
        self.lbl_pins_col.config(text=f"Coluna Ativa: {btn['col_pin']} (0V Read)")
        self.lbl_hex_code.config(text=f"HID Report Byte 2: {btn['hex']}")
        
        log_msg = f"[EVENTO PYTHON] Tecla {btn['key']} ({btn['label']}) acionada via GPIO {btn['row_pin']} + {btn['col_pin']}."
        self.lbl_log.config(text=log_msg)

        # Beep Som
        if winsound:
            try:
                winsound.Beep(880, 100)
            except Exception:
                pass

        # Disparar Ação Específica
        if btn_id == 0: # F13 - Soundboard
            self.stage_label_main.config(text="🔊\nEfeito Sonoro (Soundboard)", fg="#00f2fe")
            self.stage_label_sub.config(text="Reproduzindo vinheta de áudio sintetizada em Python...")
        elif btn_id == 1: # F14 - Mic Toggle
            self.is_mic_muted = not self.is_mic_muted
            if self.is_mic_muted:
                self.stage_label_main.config(text="🔇\nMICROFONE MUTADO", fg="#ff0844")
                self.stage_label_sub.config(text="Áudio desligado pelo Stream Deck (F14)")
            else:
                self.stage_label_main.config(text="🎙️\nMICROFONE LIGADO (ON AIR)", fg="#00e676")
                self.stage_label_sub.config(text="Transmitindo áudio para a sala de aula...")
        elif btn_id == 2: # F15 - Scenes
            scenes = ["📊 Cena 1: Slide Apresentação", "📹 Cena 2: Webcam Sala", "💻 Cena 3: Código C STM32"]
            self.scene_index = (self.scene_index + 1) % len(scenes)
            self.stage_label_main.config(text=f"🎬\n{scenes[self.scene_index]}", fg="#4facfe")
            self.stage_label_sub.config(text="Cena alternada com sucesso no alternador Python!")
        elif btn_id == 3: # F16 - Timer
            self.timer_seconds += 5
            self.stage_label_main.config(text=f"⏱️\nCronômetro: {self.timer_seconds}s", fg="#ffab00")
            self.stage_label_sub.config(text="Tempo de apresentação atualizado.")
        elif btn_id == 4: # F17 - Alert
            messagebox.showwarning("Alerta da Sala (Python)", "Notificação prioritária acionada pelo Stream Deck (F17)!")
        elif btn_id == 5: # F18 - LED
            self.stage_label_main.config(text="💡\nModo Neon / Iluminação LED", fg="#7f00ff")
            self.stage_label_sub.config(text="Efeitos visuais de iluminação alterados.")
        elif btn_id == 6: # F19 - STM32 Diagram
            self.stage_label_main.config(text="⚡\nSTM32F103C8T6 Architecture", fg="#00f2fe")
            self.stage_label_sub.config(text="ARM Cortex-M3 | 72MHz | USB Custom HID | Open-Drain Matrix")
        elif btn_id == 7: # F20 - Meme
            meme_text = MEMES[self.meme_index % len(MEMES)]
            self.meme_index += 1
            self.stage_label_main.config(text="🤖\nMeme de Embarcados", fg="#ffab00")
            self.stage_label_sub.config(text=meme_text)
        elif btn_id == 8: # F21 - Celebration
            self.stage_label_main.config(text="🎉\nAPRESENTAÇÃO CONCLUÍDA!", fg="#00e676")
            self.stage_label_sub.config(text="Parabéns equipe FEELT / UFU! Projeto aprovado!")

def main():
    root = tk.Tk()
    app = StreamDeckPythonApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
