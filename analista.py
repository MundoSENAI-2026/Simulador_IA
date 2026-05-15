import asyncio
import websockets
import json
import socket
from openai import OpenAI
import threading

# ==========================================
# LM STUDIO LOCAL
# ==========================================
client_ai = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

# ==========================================
# CONFIGURAÇÃO DOS SERVIDORES
# ==========================================
HOST = "0.0.0.0"
PORTA_TCP = 5000
PORTA_WS = 8765

# Conjunto de clientes WebSocket conectados
CLIENTES_WS = set()

async def broadcast(mensagem):
    """Envia uma mensagem para todos os clientes WebSocket conectados."""
    if CLIENTES_WS:
        payload = json.dumps(mensagem)
        await asyncio.gather(*[cliente.send(payload) for cliente in CLIENTES_WS])

async def gerenciar_websocket(websocket):
    """Adiciona e remove clientes WebSocket."""
    CLIENTES_WS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CLIENTES_WS.remove(websocket)

async def processar_dados_maquina(reader, writer):
    """Lida com as conexões TCP vindas da maquina.py."""
    endereco = writer.get_extra_info('peername')
    print(f"\n🔌 Máquina conectada: {endereco}")

    try:
        dados_recebidos = await reader.read(4096)
        if not dados_recebidos:
            return

        dados = json.loads(dados_recebidos.decode())

        # ==========================================
        # VARIÁVEIS DOS SENSORES
        # ==========================================
        temp = dados.get("temperatura_c", 0)
        pressao = dados.get("pressao", 0)
        nivel = dados.get("nivel", 0)
        ph = dados.get("ph", 0)

        # ==========================================
        # EXIBE DADOS
        # ==========================================
        print("===================================")
        print(f"🌡 Temperatura : {temp} °C")
        print(f"⚙ Pressão     : {pressao} bar")
        print(f"🧪 pH          : {ph}")
        print(f"🛢 Nível       : {nivel}%")
        print("===================================")

        # Envia dados para o frontend via WebSocket
        await broadcast({
            "tipo": "sensores",
            "dados": dados
        })

        # ==========================================
        # VERIFICA ALERTAS
        # ==========================================
        alerta = False
        if temp > 38 or pressao > 2 or ph < 6.5 or ph > 7.5 or nivel < 65:
            alerta = True

        # ==========================================
        # IA LOCAL
        # ==========================================
        if alerta:
            print("🚨 ALERTA CRÍTICO DETECTADO")
            print("🤖 Solicitando análise da IA...\n")

            # Executa a chamada da IA em uma thread separada para não travar o servidor
            loop = asyncio.get_event_loop()
            resposta = await loop.run_in_executor(None, lambda: client_ai.chat.completions.create(
                model="local-model",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um técnico industrial do SENAI especializado em automação e biorreatores. Forneça respostas técnicas, curtas e objetivas."
                    },
                    {
                        "role": "user",
                        "content": f"Analise os sensores do biorreator:\n- Temperatura: {temp} °C\n- Pressão: {pressao} bar\n- pH: {ph}\n- Nível: {nivel}%\n\nExiste risco operacional? Qual ação deve ser tomada?"
                    }
                ],
                temperature=0.4
            ))

            texto = resposta.choices[0].message.content

            print("========== ANALISE IA ==========")
            print(texto)
            print("================================")

            # Envia a análise para o frontend via WebSocket
            await broadcast({
                "tipo": "ia_analise",
                "mensagem": texto
            })

        else:
            print("✅ Sistema operando normalmente")
            # Limpa mensagem de alerta no frontend se estiver tudo ok
            await broadcast({
                "tipo": "ia_analise",
                "mensagem": "✅ Sistema operando normalmente"
            })

    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    # Inicia o servidor WebSocket
    async with websockets.serve(gerenciar_websocket, "0.0.0.0", PORTA_WS):
        # Inicia o servidor TCP
        server_tcp = await asyncio.start_server(processar_dados_maquina, HOST, PORTA_TCP)
        
        print("🚀 ANALISTA IA COM WEBSOCKET INICIADO")
        print(f"📡 Escutando TCP na porta {PORTA_TCP}")
        print(f"🌐 Servidor WebSocket na porta {PORTA_WS}\n")

        async with server_tcp:
            await server_tcp.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Sistema encerrado pelo usuário")