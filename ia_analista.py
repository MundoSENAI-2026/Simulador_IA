import paho.mqtt.client as mqtt
import json
import google.generativeai as genai

# --- CONFIGURAÇÃO IA ---
genai.configure(api_key="AIzaSyDvsg59PBPPmHMURHexrWW15CqISMpnj0s") 
model = genai.GenerativeModel('gemini-2.5-flash')

def ao_conectar(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ CONECTADO AO BROKER!")
        client.subscribe("senai/biorreator/dados")
        print("📡 Ouvindo canal: senai/biorreator/dados")
    else:
        print(f"❌ Falha na conexão. Código: {rc}")

def ao_receber_mensagem(client, userdata, msg):
    try:
        print("\n📥 DADO RECEBIDO!")
        dados = json.loads(msg.payload.decode())
        temp = dados.get('temperatura_c', 0)
        pressao = dados.get('pressao', 0)
        
        print(f"📊 Monitor: Pressão {pressao} | Temp {temp}")

        if pressao > 2.0 or temp > 38.0:
            print("🚨 CRÍTICO! Consultando Gemini...")
            prompt = f"Dados do biorreator: {dados}. Dê uma instrução curta de manutenção."
            res = model.generate_content(prompt)
            print(f"🤖 IA DIZ: {res.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")

# --- CONEXÃO ---
broker = "broker.emqx.io"
cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.on_connect = ao_conectar
cliente.on_message = ao_receber_mensagem

print("🔄 Iniciando sistema...")
cliente.connect(broker, 1883)
cliente.loop_forever() # Só um desse no final do arquivo!