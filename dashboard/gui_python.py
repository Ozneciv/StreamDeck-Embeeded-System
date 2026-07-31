"""
==============================================================================
 STREAM DECK STM32 BLUEPILL - PYTHON TKINTER GUI DASHBOARD
==============================================================================
 Interface gráfica desktop em Python (Tkinter) para visualização e teste
 das teclas de F13 a F21 enviadas pelo microcontrolador STM32.

 Como rodar:
    python dashboard/gui_python.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time

class StreamDeckPythonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stream Deck - Sistemas Embarcados - FEELT UFU (Python GUI)")
        self.root.geometry("780x620")
        self.root.configure(bg="#0a0c10")

        self.buttons_info = [
            ("F13", "0x68", "PA1 + PA4", "Soundboard SFX", "🔊"),
            ("F14", "0x69", "PA1 + PA5", "Mudo / On-Air", "🎙️"),
            ("F15", "0x6A", "PA1 + PA6", "Alternar Cena", "🎬"),
            ("F16", "0x6B", "PA2 + PA4", "Cronômetro", "⏱️"),
            ("F17", "0x6C", "PA2 + PA5", "Alerta Sala", "🔔"),
            ("F18", "0x6D", "PA2 + PA6", "Efeitos LED", "💡"),
            ("F19", "0x6E", "PA3 + PA4", "Diagrama STM32", "⚡"),
            ("F20", "0x6F", "PA3 + PA5", "Meme Embarcados", "🤖"),
            ("F21", "0x70", "PA3 + PA6", "Celebração", "🎉")
        ]

        self.create_widgets()

    def create_widgets(self):
        # Header Frame
        header = tk.Frame(self.root, bg="#12161f", height=70)
        header.pack(fill="x", side="top")
        
        lbl_title = tk.Label(header, text="Stream Deck - Sistemas Embarcados - FEELT UFU", font=("Outfit", 14, "bold"), fg="#00f2fe", bg="#12161f")
        lbl_title.pack(side="left", padx=20, pady=15)

        lbl_sub = tk.Label(header, text="Python Native Desktop GUI", font=("Fira Code", 9), fg="#8a99ad", bg="#12161f")
        lbl_sub.pack(side="right", padx=20, pady=15)

        # Team Frame
        team_frame = tk.LabelFrame(self.root, text=" Integrantes do Projeto (FEELT / UFU) ", font=("Outfit", 10, "bold"), fg="#ffab00", bg="#0a0c10", bd=1, relief="solid")
        team_frame.pack(fill="x", padx=20, pady=10)

        members = [
            "Vicenzo De Marco Olivalves (12421ECP006)",
            "Mateus Henrique Gonçalves (12311ECP021)",
            "Gustavo Martins (12111ETE002)",
            "Bruna Silva (12021ETE007)"
        ]
        for idx, m in enumerate(members):
            lbl_m = tk.Label(team_frame, text=m, font=("Outfit", 9), fg="#f0f4f8", bg="#0a0c10")
            lbl_m.grid(row=idx//2, column=idx%2, sticky="w", padx=15, pady=4)

        # 3x3 Grid Frame
        grid_frame = tk.Frame(self.root, bg="#0a0c10")
        grid_frame.pack(padx=20, pady=10)

        self.btn_widgets = []
        for idx, (key, hex_code, pins, label, icon) in enumerate(self.buttons_info):
            r, c = idx // 3, idx % 3
            btn_text = f"{icon}\n{key} ({hex_code})\n{label}"
            b = tk.Button(grid_frame, text=btn_text, font=("Outfit", 10, "bold"), fg="#f0f4f8", bg="#181d28",
                          activebackground="#00f2fe", activeforeground="#000000", bd=2, relief="groove", width=18, height=4,
                          command=lambda i=idx: self.on_button_press(i))
            b.grid(row=r, column=c, padx=8, pady=8)
            self.btn_widgets.append(b)

        # Telemetry Log
        self.lbl_log = tk.Label(self.root, text="Status: Aguardando entrada do Stream Deck...", font=("Fira Code", 9), fg="#00e676", bg="#0a0c10")
        self.lbl_log.pack(side="bottom", pady=15)

    def on_button_press(self, idx):
        key, hex_code, pins, label, icon = self.buttons_info[idx]
        timestamp = time.strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] Tecla {key} ({hex_code}) acionada! Pino: {pins} | Ação: {label}"
        self.lbl_log.config(text=log_msg)
        print(log_msg)

if __name__ == '__main__':
    root = tk.Tk()
    app = StreamDeckPythonApp(root)
    root.mainloop()
