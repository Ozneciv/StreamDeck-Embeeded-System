# -*- coding: utf-8 -*-
"""
==============================================================================
 STREAM DECK STM32 BLUEPILL - APLICAÇÃO DE INTERFACE PYTHON 3 (FEELT / UFU)
==============================================================================
 Aplicação principal em Python 3 que executa o servidor de interface e o 
 painel de acompanhamento do Stream Deck em tempo real.

 Execução no terminal:
    python app.py
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import threading
import time

PORT = 8000
DASHBOARD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard')

class StreamDeckPythonHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def log_message(self, format, *args):
        # Esconde logs HTTP repetitivos para manter o terminal limpo
        pass

def start_python_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), StreamDeckPythonHandler) as httpd:
        httpd.serve_forever()

def main():
    print("=" * 70)
    print("  STREAM DECK STM32 BLUEPILL - APLICAÇÃO EM PYTHON 3 (FEELT / UFU)")
    print("=" * 70)
    print(f"🚀 [PYTHON ENGINE] Servidor de Interface ativo na porta {PORT}")
    print("🐍 Backend: Python 3 (http.server + threading + socketserver)")
    print("🎓 Instituição: FEELT / UFU - Sistemas Embarcados I")
    print("-" * 70)

    # Inicia a thread do servidor Python
    server_thread = threading.Thread(target=start_python_server, daemon=True)
    server_thread.start()

    time.sleep(0.5)

    # Abre a interface visual que você apresentou no navegador
    url = f"http://localhost:{PORT}"
    print(f"🌐 [PYTHON APP] Abrindo a Interface do Stream Deck em: {url}")
    webbrowser.open(url)

    print("------------------------------------------------------------------")
    print("Pressione Ctrl+C para encerrar a aplicação Python.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nAplicação Python finalizada com sucesso.")

if __name__ == '__main__':
    main()
