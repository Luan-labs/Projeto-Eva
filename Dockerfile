FROM python:3.11-slim

# Variável de ambiente para evitar prompts
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

# Instala dependências do sistema se necessário
# RUN apt-get update && apt-get install -y build-essential

# Instala dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expõe a porta usada pelo Flask
ENV PORT=8080

# Comando para rodar o app
CMD ["python", "app.py"]
