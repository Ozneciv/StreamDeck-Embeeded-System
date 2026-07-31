"""
==============================================================================
 STREAM DECK STM32 BLUEPILL - PYTHON DASHBOARD & INTERFACE APPLICATION (UFU/FEELT)
==============================================================================
 Aplicação nativa em Python para simulação e monitoramento do Stream Deck
 em tempo real na sala de aula.

 Como rodar:
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

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

def start_server():
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"🚀 [PYTHON SERVER] Interface Stream Deck ativa em http://localhost:{PORT}")
        httpd.serve_forever()

def main():
    print("==================================================================")
    print("  STREAM DECK STM32 BLUEPILL - INTERFACE PYTHON (FEELT / UFU)")
    print("==================================================================")
    
    # Inicia o servidor HTTP Python em thread separada
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    time.sleep(1)
    
    # Abre automaticamente no navegador do usuário
    url = f"http://localhost:{PORT}"
    print(f"🌐 Abrindo interface gráfica Python em: {url}")
    webbrowser.open(url)
    
    print("------------------------------------------------------------------")
    print("Pressione Ctrl+C para encerrar o servidor Python.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServidor Python finalizado com sucesso.")

if __name__ == '__main__':
    main()
