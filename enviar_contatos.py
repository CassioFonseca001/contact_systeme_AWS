import sys
import requests
import pandas as pd
import openpyxl
import json
from concurrent.futures import ThreadPoolExecutor

# Configuração da API
URL = "https://api.systeme.io/api/contacts"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-API-Key": "uliwgfxc19o8p00i1nsm67wa8hze0q3nqklek6vivdjwbgyd0lt1wz2uc1h8l7z0"
}
LOCALE = "pt"

# Lendo o nome do arquivo CSV a partir do argumento
if len(sys.argv) < 2:
    print("Erro: Nenhum arquivo CSV especificado.")
    sys.exit(1)

csv_file = sys.argv[1]

# Função para salvar logs
def escrever_log(mensagem):
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(mensagem + "\n")

# Função para tratar erros 422
def tratar_erro_422(response_text):
    """Função para extrair mensagens curtas dos erros 422."""
    try:
        erro_json = json.loads(response_text)
        if "violations" in erro_json and len(erro_json["violations"]) > 0:
            return erro_json["violations"][0]["message"]
        return "Erro desconhecido 422"
    except json.JSONDecodeError:
        return "Erro no formato da resposta da API"

try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    escrever_log(f"Erro: O arquivo '{csv_file}' não foi encontrado.")
    sys.exit(1)

# Exibir colunas para depuração
escrever_log(f"📊 Colunas encontradas no CSV: {df.columns.tolist()}")

# Normalizar os nomes das colunas
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Verificar se a coluna "email" existe
if "email" not in df.columns:
    escrever_log("Erro: A coluna 'Email' não foi encontrada no arquivo CSV.")
    sys.exit(1)

# 🔹 Contadores
total_linhas = len(df)
status_422_count = 0
status_sucesso_count = 0  # Contador de e-mails cadastrados com sucesso

# Função para enviar email
def enviar_email(email):
    global status_sucesso_count, status_422_count
    payload = {
        "email": email,
        "locale": LOCALE
    }
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        if response.status_code in range(200, 300):
            escrever_log(f"✅ Enviado com sucesso para {email}")
            status_sucesso_count += 1  # Contabiliza sucesso
        elif response.status_code == 422:
            mensagem_erro = tratar_erro_422(response.text)
            escrever_log(f"⚠️ Erro 422 para {email}: {mensagem_erro}")
            status_422_count += 1  # Contabiliza erro 422
        else:
            escrever_log(f"❌ Falha ao enviar {email} - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        escrever_log(f"❌ Erro ao enviar {email}: {e}")

# 🔹 Enviar e-mails em paralelo
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(enviar_email, df["email"].dropna())

# 🔹 Registrar contagem total no final do log
escrever_log(f"📌 Total de linhas carregadas: {total_linhas}")
escrever_log(f"✅ Total de sucessos: {status_sucesso_count}")
escrever_log(f"❌ Total de erros 422: {status_422_count}")
escrever_log("🚀 Processamento concluído!")