# Projeto-Eva
# Chatbot Molecular com Claude e Flask

Este é um chatbot em Flask integrado à API da Anthropic (Claude), desenvolvido para responder perguntas sobre Biologia Molecular (DNA, RNA, proteínas, etc.).

## Funcionalidades

- Interface web simples com Flask
- Integração com a API Claude (Anthropic)
- Respostas contextuais sobre Biologia Molecular
- Fácil implantação em plataformas como Render ou Fly.io

## Tecnologias

- Python 3.11+
- Flask
- Anthropic SDK
- HTML (Jinja2 templates)
- dotenv (opcional)

## Pré-requisitos

- Python instalado
- Conta e chave de API da [Anthropic](https://www.anthropic.com/)
- Git

## Instalação local

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/nome-do-repo.git
cd nome-do-repo

## Ambiente Virtual

python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows

## Instale as dependências

pip install -r requirements.txt

## Crie um arquivo .env com sua chave da API da Anthropic:

ANTHROPIC_API_KEY=sua-chave-aqui

## Inicie o Servidor Flask
bash:
python app.py

acesse //locallhost:5000 no navegador. Deploy.






