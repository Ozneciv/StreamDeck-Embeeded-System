"""
STREAM DECK STM32 BLUEPILL - PYTHON KEYBOARD LISTENER
------------------------------------------------------
Este script em Python monitora a pressionar das teclas F13 até F21 em tempo real.
Utiliza a biblioteca 'pynput' (ou 'keyboard').

Para instalar a biblioteca necessária:
    pip install pynput
"""

import time
import sys
try:
    from pynput import keyboard
except ImportError:
    print("A biblioteca 'pynput' não está instalada. Instale com: pip install pynput")
    sys.exit(1)

# Mapeamento de Teclas Especiais F13 a F21
KEY_MAPPING = {
    keyboard.Key.f13: ("F13", "Botão 1 (0x68)", "PA1 + PA4"),
    keyboard.Key.f14: ("F14", "Botão 2 (0x69)", "PA1 + PA5"),
    keyboard.Key.f15: ("F15", "Botão 3 (0x6A)", "PA1 + PA6"),
    keyboard.Key.f16: ("F16", "Botão 4 (0x6B)", "PA2 + PA4"),
    keyboard.Key.f17: ("F17", "Botão 5 (0x6C)", "PA2 + PA5"),
    keyboard.Key.f18: ("F18", "Botão 6 (0x6D)", "PA2 + PA6"),
    keyboard.Key.f19: ("F19", "Botão 7 (0x6E)", "PA3 + PA4"),
    keyboard.Key.f20: ("F20", "Botão 8 (0x6F)", "PA3 + PA5"),
    keyboard.Key.f21: ("F21", "Botão 9 (0x70)", "PA3 + PA6")
}

def on_press(key):
    if key in KEY_MAPPING:
        name, btn, pins = KEY_MAPPING[key]
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] 🚀 TELEMETRIA STM32: {name} | {btn} | Pinos Ativos: {pins}")

def main():
    print("==========================================================")
    print("  STREAM DECK STM32 BLUEPILL - PYTHON LISTENER ATIVO")
    print("==========================================================")
    print("Aguardando pressionamento de botões no Stream Deck (F13..F21)...")
    print("Pressione Ctrl+C no terminal para encerrar.")
    print("----------------------------------------------------------")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
