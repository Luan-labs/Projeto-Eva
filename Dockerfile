# Usa uma imagem leve com Python
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do seu projeto
COPY . .

# Instala dependências
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

RUN apt-get update && apt-get install -y build-essential

# Expõe a porta 5000
EXPOSE 5000

# Comando para rodar o Flask
CMD ["python", "app.py"]
