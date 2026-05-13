import paho.mqtt.client as mqtt
import json
from openai import OpenAI

# Configura o LM Studio
ai_client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def processar_ia(client, userdata, msg):
    dados = json.loads(msg.payload.decode())
    
    # Prompt técnico baseado no seu sinótico
    prompt = (
        f"Diagnóstico Industrial BR-01: Temp={dados['temperatura_c']}°C, "
        f"Pres={dados['pressao']}kgf, Nivel={dados['nivel']}%, pH={dados['ph']}. "
        "Se houver desvio, sugira qual válvula (XV-01 a XV-07) operar. Seja curto."
    )

    try:
        response = ai_client.chat.completions.create(
            model="local-model",
            messages=[{"role": "system", "content": "Você é um Engenheiro de Automação SENAI."},
                      {"role": "user", "content": prompt}],
            temperature=0.2
        )
        diagnostico = response.choices[0].message.content
        # Envia a resposta da IA para o React
        mqtt_client.publish("senai/biorreator/ia", diagnostico)
        print(f"🤖 IA enviou diagnóstico: {diagnostico}")
    except:
        print("❌ LM Studio Offline")

mqtt_client.on_message = processar_ia
mqtt_client.connect("broker.emqx.io", 1883)
mqtt_client.subscribe("senai/biorreator/dados")
mqtt_client.loop_forever()