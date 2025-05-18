import json
import os
from flask import render_template, request, jsonify, session, redirect, url_for, flash
from app import app, db
from ai_engine import AIEngine
from models import Conversation, Message, KnowledgeEntry

# Initialize AI engine
ai_engine = AIEngine()

# Rotas para gerenciamento da base de conhecimento
@app.route('/knowledge')
def knowledge_base():
    """View knowledge base entries"""
    try:
        entries = KnowledgeEntry.query.order_by(KnowledgeEntry.category, KnowledgeEntry.language).all()
        return render_template('knowledge.html', entries=entries)
    except Exception as e:
        app.logger.error(f"Error in knowledge_base endpoint: {str(e)}")
        return "Erro ao carregar a base de conhecimento", 500

@app.route('/knowledge/sync')
def sync_knowledge():
    """Synchronize knowledge from JSON file to database"""
    try:
        # Carregar dados do arquivo JSON
        knowledge_file = "data/knowledge.json"
        with open(knowledge_file, 'r') as f:
            knowledge_data = json.load(f)
        
        # Contar entradas sincronizadas
        count = 0
        
        # Sincronizar com o banco de dados
        for entry in knowledge_data:
            # Determinar o idioma baseado na pergunta
            # Regra simples: se contém caracteres especiais do português, é pt, senão en
            language = "pt" if any(c in entry["question"].lower() for c in "áàâãéèêíìóòôõúùçñ") else "en"
            
            # Verificar se a entrada já existe
            existing = KnowledgeEntry.query.filter_by(
                question=entry["question"],
                language=language
            ).first()
            
            if existing:
                # Atualizar entrada existente
                existing.answer = entry["answer"]
                existing.category = entry["category"]
            else:
                # Criar nova entrada
                new_entry = KnowledgeEntry()
                new_entry.question = entry["question"]
                new_entry.answer = entry["answer"]
                new_entry.category = entry["category"]
                new_entry.language = language
                db.session.add(new_entry)
                count += 1
        
        # Salvar alterações
        db.session.commit()
        
        # Retornar à página da base de conhecimento com mensagem de sucesso
        message = f"Sincronização concluída com sucesso. {count} novas entradas adicionadas."
        return render_template('knowledge.html', 
                              entries=KnowledgeEntry.query.order_by(KnowledgeEntry.category, KnowledgeEntry.language).all(),
                              message=message)
    except Exception as e:
        app.logger.error(f"Error in sync_knowledge endpoint: {str(e)}")
        return "Erro ao sincronizar a base de conhecimento", 500
        
@app.route('/knowledge/view/<int:entry_id>')
def view_knowledge_entry(entry_id):
    """View a specific knowledge entry"""
    try:
        entry = KnowledgeEntry.query.get_or_404(entry_id)
        return render_template('knowledge_view.html', entry=entry)
    except Exception as e:
        app.logger.error(f"Error in view_knowledge_entry endpoint: {str(e)}")
        return "Erro ao visualizar entrada da base de conhecimento", 500

@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/history')
def history():
    """View conversation history"""
    try:
        # Obter as conversas do usuário atual
        conversations = Conversation.query.filter_by(
            user_id=session.get('user_id')
        ).order_by(Conversation.started_at.desc()).all()
        
        # Preparar dados para a visualização
        history_data = []
        for conv in conversations:
            messages = Message.query.filter_by(
                conversation_id=conv.id
            ).order_by(Message.timestamp).all()
            
            if messages:
                # Pegar a primeira mensagem como preview
                preview = next((msg.content for msg in messages if msg.role == 'user'), "Conversa sem mensagens")
                if len(preview) > 50:
                    preview = preview[:50] + "..."
                
                history_data.append({
                    'id': conv.id,
                    'date': conv.started_at.strftime('%d/%m/%Y %H:%M'),
                    'preview': preview,
                    'message_count': len(messages)
                })
        
        return render_template('history.html', conversations=history_data)
    except Exception as e:
        app.logger.error(f"Error in history endpoint: {str(e)}")
        return "Erro ao carregar o histórico de conversas", 500

@app.route('/conversation/<int:conversation_id>')
def view_conversation(conversation_id):
    """View a specific conversation"""
    try:
        # Verificar se a conversa existe
        conversation = Conversation.query.get_or_404(conversation_id)
        
        # Obter mensagens da conversa
        messages = Message.query.filter_by(
            conversation_id=conversation.id
        ).order_by(Message.timestamp).all()
        
        # Converter para formato de exibição
        message_data = []
        for msg in messages:
            message_data.append({
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.strftime('%H:%M:%S')
            })
        
        # Dados da conversa
        conversation_data = {
            'id': conversation.id,
            'date': conversation.started_at.strftime('%d/%m/%Y %H:%M'),
            'messages': message_data
        }
        
        return render_template('conversation.html', conversation=conversation_data)
    except Exception as e:
        app.logger.error(f"Error in view_conversation endpoint: {str(e)}")
        return "Erro ao carregar a conversa", 500

@app.route('/chat', methods=['POST'])
def chat():
    """Process user message and generate AI response"""
    try:
        user_message = request.json.get('message', '')
        
        # Get conversation ID from session or create a new one
        if 'conversation_id' not in session:
            # Create a new conversation
            conversation = Conversation()
            conversation.user_id = session.get('user_id')
            db.session.add(conversation)
            db.session.commit()
            session['conversation_id'] = conversation.id
            session['conversation'] = []
        else:
            # Get existing conversation
            conversation = Conversation.query.get(session['conversation_id'])
            if not conversation:
                # Create new if not found
                conversation = Conversation()
                conversation.user_id = session.get('user_id')
                db.session.add(conversation)
                db.session.commit()
                session['conversation_id'] = conversation.id
                session['conversation'] = []
        
        # Add user message to conversation history in session
        session['conversation'].append({"role": "user", "content": user_message})
        
        # Save user message to database
        user_msg = Message()
        user_msg.content = user_message
        user_msg.role = "user"
        user_msg.conversation_id = conversation.id
        db.session.add(user_msg)
        db.session.commit()
        
        # Generate AI response
        response = ai_engine.generate_response(user_message, session['conversation'])
        
        # Add AI response to conversation history in session
        session['conversation'].append({"role": "assistant", "content": response})
        
        # Save AI response to database
        ai_msg = Message()
        ai_msg.content = response
        ai_msg.role = "assistant"
        ai_msg.conversation_id = conversation.id
        db.session.add(ai_msg)
        db.session.commit()
        
        # Limit conversation history to last 20 messages in session
        if len(session['conversation']) > 20:
            session['conversation'] = session['conversation'][-20:]
        
        # Persist the session
        session.modified = True
        
        return jsonify({'response': response})
    
    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'response': "Peço desculpas, mas estou tendo problemas para processar sua solicitação no momento."}), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation history"""
    try:
        # Limpar a sessão atual
        session['conversation'] = []
        
        # Iniciar uma nova conversa no banco de dados
        conversation = Conversation()
        conversation.user_id = session.get('user_id')
        db.session.add(conversation)
        db.session.commit()
        session['conversation_id'] = conversation.id
        
        session.modified = True
        return jsonify({'status': 'success', 'message': 'Conversa reiniciada com sucesso'})
    except Exception as e:
        app.logger.error(f"Error in reset endpoint: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500