import paho.mqtt.client as mqtt
import json
import time
import random

# Configurações do Broker
BROKER = "broker.emqx.io" 
TOPICO = "senai/biorreator/dados"

# ID de cliente único para o simulador
cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Simulador_BR01_Completo")

print(f"🔄 Conectando ao broker {BROKER}...")

try:
    cliente.connect(BROKER, 1883)
    cliente.loop_start()
    print("✅ MÁQUINA TRANSMITINDO DADOS COMPLETOS (TIT, PIT, LIT, AIT)!")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    exit()

while True:
    # Gerando dados baseados na Lista de Instrumentos
    dados = {
        "temperatura_c": round(random.uniform(34, 41), 1), # TIT_100_01
        "pressao": round(random.uniform(1.0, 2.5), 2),     # PIT_100_01
        "nivel": round(random.uniform(60, 85), 1),         # LIT_100_01
        "ph": round(random.uniform(6.2, 7.8), 1)           # AIT_100_01
    }
    
    # Publica no tópico
    cliente.publish(TOPICO, json.dumps(dados))
    print(f"📡 Enviado para o Supervisório: {dados}")
    
    # Ajustado para 10 segundos conforme solicitado
    time.sleep(10)