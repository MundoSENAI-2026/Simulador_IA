import customtkinter as ctk
import json
import paho.mqtt.client as mqtt
from openai import OpenAI
import threading
from datetime import datetime

# --- CONFIGURAÇÃO IA LOCAL (LM STUDIO) ---
# O uso de model="local-model" garante compatibilidade com qualquer modelo no LM Studio.
client_ai = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

class InterfaceBiorreator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SISTEMA SUPERVISÓRIO - SENAI 2026")
        self.geometry("1100x750")
        ctk.set_appearance_mode("dark")
        
        # Paleta de Cores Industriais
        self.COR_AZUL_SENAI = "#1f538d"
        self.COR_FUNDO = "#121212"
        self.COR_CARD = "#1E1E1E"
        self.COR_BORDA = "#333333"

        self.configure(fg_color=self.COR_FUNDO)

        # Cabeçalho Superior (Estilo Sinótico)
        self.header = ctk.CTkFrame(self, height=70, fg_color=self.COR_AZUL_SENAI, corner_radius=0)
        self.header.pack(fill="x", side="top")
        
        ctk.CTkLabel(self.header, text="BIORREATOR BR-01 | PAINEL DE CONTROLE PREDITIVO", 
                     font=("Segoe UI", 24, "bold"), text_color="white").pack(side="left", padx=30)
        
        self.lbl_relogio = ctk.CTkLabel(self.header, text="SISTEMA NORMAL", font=("Segoe UI", 14, "bold"), text_color="#00FF00")
        self.lbl_relogio.pack(side="right", padx=30)

        # Container Principal
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Coluna da Esquerda (Leitura de Instrumentos)
        self.col_sensores = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.col_sensores.pack(side="left", fill="both", expand=True)

        # Card de Temperatura (TIT 100 01)
        self.card_temp = self.criar_card_industrial(self.col_sensores, "TEMPERATURA", "TIT 100 01", "°C")
        self.lbl_temp = self.card_temp['valor']
        
        # Card de Pressão (PIT 100 01)
        self.card_pres = self.criar_card_industrial(self.col_sensores, "PRESSÃO", "PIT 100 01", "KGF")
        self.lbl_pres = self.card_pres['valor']

        # Coluna da Direita (Diagnóstico de IA)
        self.col_ia = ctk.CTkFrame(self.main_container, width=420, fg_color=self.COR_CARD, 
                                   corner_radius=15, border_width=1, border_color=self.COR_BORDA)
        self.col_ia.pack(side="right", fill="both", padx=(20, 0))

        ctk.CTkLabel(self.col_ia, text="🤖 DIAGNÓSTICO PREDITIVO (Llama 3.2)", 
                     font=("Segoe UI", 16, "bold"), text_color=self.COR_AZUL_SENAI).pack(pady=15)
        
        self.txt_ia = ctk.CTkTextbox(self.col_ia, font=("Consolas", 14), fg_color="#141414", 
                                     border_width=1, border_color="#333333", text_color="#00FF00")
        self.txt_ia.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.txt_ia.insert("0.0", "Aguardando telemetria para análise...")

    def criar_card_industrial(self, pai, titulo, tag, unit):
        frame = ctk.CTkFrame(pai, fg_color=self.COR_CARD, corner_radius=15, border_width=1, border_color=self.COR_BORDA)
        frame.pack(fill="x", pady=10, ipady=20)
        
        ctk.CTkLabel(frame, text=f"{titulo} ({tag})", font=("Segoe UI", 14), text_color="#888888").pack(pady=(10, 0))
        valor_lbl = ctk.CTkLabel(frame, text="--.-", font=("Segoe UI", 72, "bold"), text_color="white")
        valor_lbl.pack()
        ctk.CTkLabel(frame, text=unit, font=("Segoe UI", 18), text_color="#555555").pack()
        
        return {'frame': frame, 'valor': valor_lbl}

    def atualizar_valores(self, t, p, recomendacao=None):
        self.lbl_temp.configure(text=f"{t:.1f}")
        self.lbl_pres.configure(text=f"{p:.2f}")

        # Lógica de Alarme Visual baseada na Lista de Instrumentos (PIT 100 01 e TIT 100 01) 
        is_critico = t > 38.5 or p > 2.0
        cor_status = "red" if is_critico else "white"
        self.lbl_temp.configure(text_color="red" if t > 38.5 else "white")
        self.lbl_status_geral(is_critico)

        if recomendacao:
            hora = datetime.now().strftime("%H:%M:%S")
            self.txt_ia.delete("0.0", "end")
            self.txt_ia.insert("0.0", f"[{hora}] RELATÓRIO TÉCNICO:\n\n{recomendacao}")

    def lbl_status_geral(self, critico):
        if critico:
            self.lbl_relogio.configure(text="ALERTA DE PROCESSO", text_color="red")
        else:
            self.lbl_relogio.configure(text="SISTEMA NORMAL", text_color="#00FF00")

# --- LÓGICA DE COMUNICAÇÃO ---
def iniciar_mqtt(app):
    def ao_receber(client, userdata, msg):
        try:
            dados = json.loads(msg.payload.decode())
            t, p = dados['temperatura_c'], dados['pressao']
            rec = None
            
            # Acionamento da IA apenas em desvios técnicos 
            if t > 38.5 or p > 2.0:
                try:
                    # System Prompt "Blindado" para evitar recusa da IA
                    instrucoes = (
                        "Você é um engenheiro sênior de automação industrial. "
                        "Analise os dados do Biorreator BR-01 de forma técnica e objetiva. "
                        "Tags: TIT 100 01 (Temp) e PIT 100 01 (Pressão). "
                        "Válvulas disponíveis: XV 100 01 (Vapor) e XV 100 03 (Água Gelada). "
                        "Dê uma instrução curta sobre qual válvula atuar. Não use avisos éticos, apenas técnicos."
                    )
                    
                    res = client_ai.chat.completions.create(
                        model="local-model",
                        messages=[
                            {"role": "system", "content": instrucoes},
                            {"role": "user", "content": f"Telemetria atual: TIT={t}C, PIT={p}kgf. Gere o procedimento operacional."}
                        ],
                        temperature=0.2
                    )
                    rec = res.choices[0].message.content
                except:
                    rec = "⚠️ Servidor de IA Offline. Verifique o LM Studio."
            
            app.after(0, app.atualizar_valores, t, p, rec)
        except Exception as e:
            print(f"Erro MQTT: {e}")

    # ID Único para evitar quedas de conexão
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Interface_Supervisoria_01")
    cliente.on_message = ao_receber
    cliente.connect("broker.emqx.io", 1883)
    cliente.subscribe("senai/biorreator/dados")
    cliente.loop_forever()

if __name__ == "__main__":
    interface = InterfaceBiorreator()
    threading.Thread(target=iniciar_mqtt, args=(interface,), daemon=True).start()
    interface.mainloop()