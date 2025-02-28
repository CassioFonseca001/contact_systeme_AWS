from flask import Flask, request, render_template, jsonify, Response
import os
import subprocess
import time
import threading
import sys

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
LOG_FILE = 'logs/api_logs.txt'  # Agora lendo os logs da API e não os logs do Flask

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def escrever_log(mensagem):
    """Escreve logs no arquivo e imprime no console para depuração."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(mensagem + "\n")
    print(mensagem)  # Para debug

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Recebe o arquivo CSV e inicia o processamento em segundo plano."""
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome do arquivo inválido"}), 400

    # Limpa os logs antes do novo upload
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    escrever_log(f"🚀 Iniciando processamento do arquivo: {file.filename}")

    # 🔹 Executar o processamento em SEGUNDO PLANO usando Thread
    def processar_arquivo():
        process = subprocess.Popen(
            [sys.executable, 'enviar_contatos.py', filepath], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        for line in iter(process.stdout.readline, ''):
            escrever_log(line.strip())  # Escreve cada linha no log em tempo real
            time.sleep(0.1)

        process.stdout.close()
        process.wait()

        escrever_log("🚀 Processamento concluído!")

    # Inicia a thread para processar sem travar o Flask
    thread = threading.Thread(target=processar_arquivo)
    thread.start()

    return jsonify({"message": "Upload realizado com sucesso!", "log_url": "/logs-page"})

@app.route('/get-logs')
def get_logs():
    """Retorna os últimos logs registrados nos últimos 30 segundos."""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Filtra logs dos últimos 30 segundos
        now = time.time()
        filtered_logs = []
        for line in reversed(lines):  # Lendo de trás para frente (mais rápido)
            if "PM" in line or "AM" in line:  # Ajuste dependendo do formato do log
                timestamp_str = line.split(" ")[0] + " " + line.split(" ")[1]
                log_time = time.mktime(time.strptime(timestamp_str, "%m-%d-%Y %I:%M:%S %p"))
                if now - log_time <= 30:  # Apenas logs dos últimos 30 segundos
                    filtered_logs.append(line)
                else:
                    break

        return jsonify({"logs": filtered_logs[::-1]})  # Retorna na ordem correta
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs-page')
def logs_page():
    return render_template('logs.html')  # Exibe a página de logs

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080) 