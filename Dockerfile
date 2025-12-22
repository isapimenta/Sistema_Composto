FROM python:3.11-slim

WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para o banco de dados
RUN mkdir -p /app/instance

# Expor porta
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "app.py"]