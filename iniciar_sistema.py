import subprocess
import os
import sys

# ==========================================
# CAMINHO DOS ARQUIVOS
# ==========================================
PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))

analista = os.path.join(PASTA_PROJETO, "analista.py")
maquina = os.path.join(PASTA_PROJETO, "maquina.py")

print("🚀 Iniciando sistema completo...\n")

# ==========================================
# ABRE TERMINAL DO ANALISTA
# ==========================================
subprocess.Popen(
    f'start cmd /k python "{analista}"',
    shell=True
)

print("✅ Analista iniciado")

# ==========================================
# ABRE TERMINAL DA MAQUINA
# ==========================================
subprocess.Popen(
    f'start cmd /k python "{maquina}"',
    shell=True
)

print("✅ Máquina iniciada")

print("\n🎯 Sistema operacional!")