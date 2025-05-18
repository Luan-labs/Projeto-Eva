from app import app
import anthropic
import os
# Import models para criar as tabelas
from app import db
import models  # noqa: F401
# Initialize the client with import osmy_secret = os.environ['ANTHROPIC_KEY_CLIENT']API key
client = anthropic.Anthropic(api_key="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")

def conversar_com_claude(mensagem):
    # Adiciona contexto sobre o nome Eve
    if "nome" in mensagem.lower() or "chama" in mensagem.lower():
        context = "Você é uma assistente chamada Eve. Sempre que perguntarem seu nome, responda que seu nome é Eve. "
        mensagem = context + mensagem
    
    resposta = client.messages.create(
        model="claude-3-opus-20240229",  # ou "claude-3-sonnet-20240229" (mais rápido e barato)
        max_tokens=1000,
        messages=[
            {"role": "user", "content": mensagem}
        ]
    )
    return resposta.content

# Loop de conversa
print("Eve: Olá! Sou a Eve, como posso ajudar?")
while True:
    entrada = input("Você: ")
    if entrada.lower() in ['sair', 'tchau', 'adeus']:
        print("Eve: Até logo!")
        break
    resposta = conversar_com_claude(entrada)
    print("Eve:", resposta)


# Criar as tabelas quando o app for inicializado
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
