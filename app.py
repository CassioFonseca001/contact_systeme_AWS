from flask import Flask, request, render_template, jsonify, Response
import os
import subprocess
import time
import threading

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
LOG_FILE = 'logs.txt'

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

    # Limpa o logs.txt antes do novo upload
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    escrever_log(f"🚀 Iniciando processamento do arquivo: {file.filename}")

    # 🔹 Executar o processamento em SEGUNDO PLANO usando Thread
    def processar_arquivo():
        process = subprocess.Popen(
            ['python3', 'enviar_contatos.py', filepath], 
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

@app.route('/stream-logs')
def stream_logs():
    """Faz streaming dos logs em tempo real para o frontend."""
    def gerar_logs():
        """Lê e transmite os logs continuamente."""
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            while True:
                line = f.readline()
                if line:
                    yield f"data: {line}\n\n"
                time.sleep(1)  # Aguarda um pouco antes de verificar novamente

    return Response(gerar_logs(), mimetype='text/event-stream')

@app.route('/logs-page')
def logs_page():
    return render_template('logs.html')  # Exibe a página de logs