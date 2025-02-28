import sys
import requests
import pandas as pd
import openpyxl
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import logging

# Configuração do Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/api_logs.txt", encoding="utf-8"),  # Novo log separado para API
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_logger")

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
    logger.error("Erro: Nenhum arquivo CSV especificado.")
    sys.exit(1)

csv_file = sys.argv[1]

try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    logger.error(f"Erro: O arquivo '{csv_file}' não foi encontrado.")
    sys.exit(1)

logger.info(f"📊 Colunas encontradas no CSV: {df.columns.tolist()}")

# Normalizar os nomes das colunas
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

if "email" not in df.columns:
    logger.error("Erro: A coluna 'Email' não foi encontrada no arquivo CSV.")
    sys.exit(1)

# Contadores
total_linhas = len(df)
status_422_count = 0
status_sucesso_count = 0  
lock = Lock()

def tratar_erro_422(response_text):
    try:
        erro_json = json.loads(response_text)
        if "violations" in erro_json and len(erro_json["violations"]) > 0:
            return erro_json["violations"][0]["message"]
        return "Erro desconhecido 422"
    except json.JSONDecodeError:
        return "Erro no formato da resposta da API"

def enviar_email(email):
    global status_sucesso_count, status_422_count
    
    payload = {
        "email": email,
        "locale": LOCALE
    }

    tentativas = 3
    for tentativa in range(1, tentativas + 1):
        try:
            response = requests.post(URL, json=payload, headers=HEADERS, timeout=10)
            response_data = response.json()

            if response.status_code in range(200, 300):
                with lock:
                    status_sucesso_count += 1  
                logger.info(f"✅ {email} cadastrado com sucesso na tentativa {tentativa}: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                return
            elif response.status_code == 422:
                mensagem_erro = tratar_erro_422(response.text)
                with lock:
                    status_422_count += 1  
                logger.warning(f"⚠️ Erro 422 para {email}: {mensagem_erro}")
                return  
            else:
                logger.error(f"❌ Falha ao enviar {email} - Status: {response.status_code}, Resposta: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro ao enviar {email} na tentativa {tentativa}: {e}")
        time.sleep(2)

    logger.error(f"❌ {email} falhou após {tentativas} tentativas.")

max_threads = min(10, len(df))
with ThreadPoolExecutor(max_workers=max_threads) as executor:
    futures = {executor.submit(enviar_email, email): email for email in df["email"].dropna()}
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")

logger.info(f"📌 Total de linhas carregadas: {total_linhas}")
logger.info(f"✅ Total de sucessos: {status_sucesso_count}")
logger.info(f"❌ Total de erros 422: {status_422_count}")
logger.info("🚀 Processamento concluído!")
