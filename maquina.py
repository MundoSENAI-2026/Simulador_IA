import paho.mqtt.client as mqtt
import json
import time
import random

# Configurações do Broker
BROKER = "broker.emqx.io" 
TOPICO = "senai/biorreator/dados"

# ID de cliente único para o simulador
cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Simulador_BR01_Sertaozinho")

print(f"🔄 Conectando ao broker {BROKER}...")

try:
    cliente.connect(BROKER, 1883)
    cliente.loop_start()
    print("✅ MÁQUINA TRANSMITINDO DADOS!")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    exit()

while True:
    # Gerando dados baseados na faixa de operação real
    dados = {
        "temperatura_c": round(random.uniform(34, 41), 1),
        "pressao": round(random.uniform(1.0, 3.0), 2)
    }
    
    # Publica no tópico que a interface está ouvindo
    cliente.publish(TOPICO, json.dumps(dados))
    print(f"📡 Enviado: {dados}")
    time.sleep(5) # Envia a cada 5 segundos