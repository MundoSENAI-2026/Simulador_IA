import socket
import json
import time
import random

# =========================
# CONFIGURAÇÃO DA REDE LOCAL
# =========================

# IP do computador que roda o analista.py
HOST = "127.0.0.1"

# Porta usada pelo analista
PORTA = 5000

print("🚀 MÁQUINA INDUSTRIAL INICIADA")
print(f"📡 Enviando dados para {HOST}:{PORTA}")

while True:

    # =========================
    # SIMULAÇÃO DOS SENSORES
    # =========================
    dados = {

        # TIT_100_01
        "temperatura_c": round(random.uniform(34, 41), 1),

        # PIT_100_01
        "pressao": round(random.uniform(1.0, 2.5), 2),

        # LIT_100_01
        "nivel": round(random.uniform(60, 85), 1),

        # AIT_100_01
        "ph": round(random.uniform(6.2, 7.8), 1)

    }

    try:

        # =========================
        # CONEXÃO COM ANALISTA
        # =========================
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        cliente.connect((HOST, PORTA))

        # Envia os dados
        cliente.send(json.dumps(dados).encode())

        print(f"📤 Dados enviados: {dados}")

        cliente.close()

    except Exception as e:

        print(f"❌ Erro de conexão: {e}")

    # =========================
    # INTERVALO
    # =========================
    time.sleep(10)