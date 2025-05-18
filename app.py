# Este arquivo está sendo mantido apenas para compatibilidade
# Todo o código foi movido para app/__init__.py e app/routes.py
# app.py
from flask import Flask, request, render_template
from anthropic import Anthropic
import os
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
app = Flask(__name__)

# Criação do cliente com a chave da API
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        prompt = request.form["prompt"]
        resposta = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return render_template("index.html", resposta=resposta.content[0].text)
    return render_template("index.html")

# Importar a aplicação do novo pacote

