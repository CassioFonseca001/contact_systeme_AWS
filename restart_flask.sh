#!/bin/bash

# Caminho do diretório do projeto Flask
PROJECT_DIR="/home/ubuntu/contact_systeme_AWS"

# Nome do ambiente virtual
VENV_DIR="$PROJECT_DIR/venv"

# Arquivo de log
LOG_FILE="$PROJECT_DIR/flask.log"

echo "🔄 Reiniciando o Flask..."

# Parar qualquer instância rodando
pkill -f flask

# Aguardar um momento para garantir que os processos foram encerrados
sleep 2

# Ativar o ambiente virtual
source "$VENV_DIR/bin/activate"

# Navegar até o diretório do projeto
cd "$PROJECT_DIR"

# Rodar o Flask em segundo plano e salvar logs
nohup python3 app.py > "$LOG_FILE" 2>&1 &

echo "✅ Flask reiniciado com sucesso!"
echo "📜 Logs podem ser encontrados em: $LOG_FILE"