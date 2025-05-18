import random
import logging
import re

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Generates responses for different types of user inputs
    """
    
    def __init__(self):
        """Initialize response templates and utilities"""
        # Generic response templates (Portuguese)
        self.generic_responses = {
            "greeting": [
                "Olá! Como posso ajudá-lo hoje?",
                "Oi! Em que posso ajudar?",
                "Saudações! Como posso ser útil?",
                "Olá! Estou aqui para ajudar. O que você precisa?"
            ],
            "farewell": [
                "Adeus! Sinta-se à vontade para conversar novamente a qualquer momento.",
                "Até logo! Foi bom conversar com você.",
                "Tchau por enquanto! Tenha um ótimo dia!",
                "Até mais! Estarei aqui se precisar de mim."
            ],
            "unknown": [
                "Não tenho certeza se entendi. Você poderia reformular?",
                "Não tenho essa informação na minha base de conhecimento.",
                "Não sei a resposta para essa pergunta.",
                "Ainda estou aprendendo e não tenho uma resposta para isso ainda."
            ],
            "conversation": [
                "Esse é um ponto interessante.",
                "Eu aprecio seus pensamentos sobre isso.",
                "Entendo o que você está dizendo.",
                "Obrigado por compartilhar isso comigo."
            ],
            "question": [
                "Deixe-me tentar responder isso para você.",
                "Aqui está o que sei sobre isso:",
                "Com base no meu conhecimento:",
                "Posso fornecer estas informações:"
            ],
            "command": [
                "Vou tentar ajudar com isso.",
                "Vamos ver o que posso fazer.",
                "Farei o meu melhor para ajudar com isso.",
                "Estou processando sua solicitação."
            ],
            "clarification": [
                "Você poderia fornecer mais detalhes?",
                "Não tenho certeza se entendi. Você pode explicar melhor?",
                "Você pode ser mais específico?",
                "Preciso de mais informações para ajudá-lo adequadamente."
            ]
        }
        
        logger.info("Response generator initialized")
    
    def generate_from_knowledge(self, knowledge_entries, entities=None):
        """
        Generate a response based on retrieved knowledge
        
        Args:
            knowledge_entries (list): Relevant knowledge entries
            entities (list, optional): Extracted entities
            
        Returns:
            str: Generated response
        """
        try:
            if not knowledge_entries:
                return self.generate_unknown_response()
            
            # Get the most relevant entry (first one)
            entry = knowledge_entries[0]
            
            # Start with the answer from the knowledge base
            response = entry["answer"]
            
            # Add a lead-in phrase occasionally for variety
            if random.random() < 0.3:
                lead_in = random.choice(self.generic_responses["question"])
                response = f"{lead_in} {response}"
            
            # Add a follow-up if we have more than one relevant entry
            if len(knowledge_entries) > 1 and random.random() < 0.3:
                response += " Posso fornecer mais informações se você estiver interessado."
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating knowledge response: {str(e)}")
            return self.generate_unknown_response()
    
    def generate_unknown_response(self):
        """
        Generate a response for when no information is available
        
        Returns:
            str: Generated response
        """
        return random.choice(self.generic_responses["unknown"])
    
    def generate_generic_response(self, intent):
        """
        Generate a generic response based on intent
        
        Args:
            intent (str): The classified intent
            
        Returns:
            str: Generated response
        """
        try:
            if intent in self.generic_responses:
                return random.choice(self.generic_responses[intent])
            else:
                return random.choice(self.generic_responses["conversation"])
        
        except Exception as e:
            logger.error(f"Error generating generic response: {str(e)}")
            return "Desculpe, estou com dificuldades para entender no momento."
    
    def generate_contextual_response(self, user_input, context):
        """
        Generate a response that considers conversation context
        
        Args:
            user_input (str): Processed user input
            context (dict): Extracted context information
            
        Returns:
            str: Generated contextual response
        """
        try:
            # Check if this is a follow-up to a previous question
            if context.get("last_question") and ("more" in user_input or "mais" in user_input):
                return "Já compartilhei o que sei sobre esse tópico. Há algo específico que você gostaria de saber mais?"
            
            # Check if topic is in our knowledge set
            if context.get("topics"):
                relevant_topic = None
                for topic in context["topics"]:
                    if topic in user_input:
                        relevant_topic = topic
                        break
                
                if relevant_topic:
                    return f"Vejo que você está interessado em {relevant_topic}. Qual aspecto específico você gostaria de saber?"
            
            # Default to a conversational response
            return self.generate_generic_response("conversation")
        
        except Exception as e:
            logger.error(f"Error generating contextual response: {str(e)}")
            return "Estou tentando entender o contexto. Você poderia reformular isso?"
