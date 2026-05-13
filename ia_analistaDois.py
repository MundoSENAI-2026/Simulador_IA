from openai import OpenAI
import json
import paho.mqtt.client as mqtt

# Configura o Python para falar com o LM Studio
# Dica: Verifique se no LM Studio o servidor está em 127.0.0.1:1234
client_ai = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

def ao_conectar(client, userdata, connect_flags, reason_code, properties):
    if reason_code == 0:
        print("✅ CONECTADO AO BROKER MQTT!")
        # O TÓPICO DEVE SER IGUAL AO DA MAQUINA
        client.subscribe("senai/biorreator/dados")
        print("📡 Inscrito no tópico: senai/biorreator/dados")
    else:
        print(f"❌ Falha na conexão: {reason_code}")

def ao_receber_mensagem(client, userdata, msg):
    try:
        dados = json.loads(msg.payload.decode())
        temp = dados.get('temperatura_c', 0)
        pressao = dados.get('pressao', 0)
        
        print(f"\n📥 DADO RECEBIDO -> Temp: {temp} | Pressão: {pressao}")

        if temp > 38.0 or pressao > 2.0:
            print("🚨 Alerta Crítico! Solicitando análise ao LM Studio...")
            
            completion = client_ai.chat.completions.create(
                model="local-model", 
                messages=[
                    {"role": "system", "content": "Você é um técnico do SENAI. Dê instruções técnicas curtas."},
                    {"role": "user", "content": f"O biorreator está com {temp}°C e {pressao} bar. O que fazer?"}
                ],
                temperature=0.7,
            )
            
            print(f"🤖 IA LOCAL DIZ: {completion.choices[0].message.content}")
            
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")

# --- CONEXÃO ---
broker = "broker.emqx.io"
cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.on_connect = ao_conectar
cliente.on_message = ao_receber_mensagem

print("🔄 Iniciando sistema analista local...")
cliente.connect(broker, 1883)
cliente.loop_forever()