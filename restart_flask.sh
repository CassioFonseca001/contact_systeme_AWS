#!/bin/bash

# Caminho do diretório do projeto Flask
PROJECT_DIR="/home/ubuntu/contact_systeme_AWS"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/flask.log"

# Função para verificar se o Flask está rodando e se a porta 5000 está em uso
verificar_status() {
    echo "🔄 Verificando se o Flask está rodando..."
    pgrep -fl flask || echo "❌ Flask não está rodando."
    
    echo "🔄 Verificando se a porta 5000 está em uso..."
    sudo netstat -tulnp | grep 5000 || echo "❌ Porta 5000 não está em uso."
}

# Verificar status antes de reiniciar
verificar_status

echo "🔄 Reiniciando o Flask..."

# Parar qualquer instância rodando
pkill -f flask 2>/dev/null && echo "✅ Flask parado." || echo "⚠️ Nenhuma instância Flask em execução."

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

# Verificar status após reiniciar
verificar_status
