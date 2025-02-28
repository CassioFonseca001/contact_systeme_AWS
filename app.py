import csv
import io
import json
import os
import requests
from flask import Flask, request, render_template, flash, redirect

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "sua_chave_secreta")

# Configuração da API do Systeme.io
API_URL = "https://api.systeme.io/api/contacts"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-API-Key": os.environ.get("X_API_KEY")
}
LOCALE = "pt"

@app.route("/", methods=["GET", "POST"])
def upload_csv():
    if request.method == "POST":
        if "csv_file" not in request.files:
            flash("Nenhum arquivo enviado.", "error")
            return redirect(request.url)
        
        file = request.files["csv_file"]
        if file.filename == "":
            flash("Nenhum arquivo selecionado.", "error")
            return redirect(request.url)

        try:
            stream = io.StringIO(file.stream.read().decode("utf-8"))
            csv_reader = csv.DictReader(stream)

            for row in csv_reader:
                payload = {
                    "email": row.get("email"),
                    "name": row.get("nome"),
                    "locale": LOCALE
                }
                response = requests.post(API_URL, headers=HEADERS, json=payload)
                
                if response.status_code != 200:
                    flash(f"Erro ao enviar {payload['email']}: {response.text}", "error")
                else:
                    flash(f"Contato {payload['email']} enviado com sucesso!", "success")

            return redirect(request.url)

        except Exception as e:
            flash(f"Erro ao processar o arquivo: {str(e)}", "error")
            return redirect(request.url)

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)