# Usa uma imagem mínima do Python para otimizar o tamanho do container
FROM python:3.9-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependências para dentro do container
COPY requirements.txt .

# Atualiza o pip e instala as dependências necessárias
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos do projeto para o diretório de trabalho
COPY . .

# Expor a porta usada pela aplicação Flask
EXPOSE 5000

# Define o comando para iniciar a aplicação no container usando Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]