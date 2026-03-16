FROM python:3.10-slim

WORKDIR /app

# Copiar dependências
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar script
COPY main.py .

# Executar a aplicação
CMD ["python", "main.py"]