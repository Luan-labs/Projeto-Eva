import logging
import random
from knowledge_base import KnowledgeBase
from nlp_utils import NLPProcessor
from response_generator import ResponseGenerator

logger = logging.getLogger(__name__)

class AIEngine:
    """Main AI engine that coordinates between different components"""
    
    def __init__(self):
        """Initialize the AI engine components"""
        logger.info("Initializing AI Engine...")
        self.knowledge_base = KnowledgeBase()
        self.nlp_processor = NLPProcessor()
        self.response_generator = ResponseGenerator()
        logger.info("AI Engine initialization complete")
    
    def generate_response(self, user_input, conversation_history):
        """
        Generate a response based on user input and conversation history
        
        Args:
            user_input (str): The user's message
            conversation_history (list): List of previous messages
            
        Returns:
            str: The AI's response
        """
        try:
            # Process the user input
            processed_input = self.nlp_processor.preprocess_text(user_input)
            
            # Determine intent
            intent = self.nlp_processor.classify_intent(processed_input)
            logger.debug(f"Classified intent: {intent}")
            
            # Extract entities if needed
            entities = self.nlp_processor.extract_entities(processed_input)
            logger.debug(f"Extracted entities: {entities}")
            
            # Handle different intents
            if intent == "greeting":
                return self._handle_greeting()
            elif intent == "farewell":
                return self._handle_farewell()
            elif intent == "question":
                return self._handle_question(processed_input, entities)
            elif intent == "command":
                return self._handle_command(processed_input, entities)
            elif intent == "conversation":
                return self._handle_conversation(processed_input, conversation_history)
            else:
                # Default response generation
                return self.response_generator.generate_generic_response(intent)
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "Peço desculpas, mas estou tendo problemas para processar sua solicitação no momento."
    
    def _handle_greeting(self):
        """Handle greeting intents"""
        greetings = [
            "Olá! Como posso ajudar você hoje?",
            "Oi! Em que posso ajudá-lo?",
            "Saudações! O que você gostaria de saber?",
            "Olá! Sou seu assistente de IA. Como posso ajudá-lo?"
        ]
        return random.choice(greetings)
    
    def _handle_farewell(self):
        """Handle farewell intents"""
        farewells = [
            "Adeus! Sinta-se à vontade para retornar se tiver mais perguntas.",
            "Até logo! Tenha um ótimo dia!",
            "Até a próxima! Cuide-se.",
            "Tchau por enquanto! Estarei aqui se precisar de ajuda mais tarde."
        ]
        return random.choice(farewells)
    
    def _handle_question(self, processed_input, entities):
        """Handle question intents"""
        # Search knowledge base for relevant information
        relevant_info = self.knowledge_base.search(processed_input)
        
        if relevant_info:
            # Generate response based on retrieved information
            return self.response_generator.generate_from_knowledge(relevant_info, entities)
        else:
            # No relevant information found
            return self.response_generator.generate_unknown_response()
    
    def _handle_command(self, processed_input, entities):
        """Handle command intents"""
        # Identify the type of command
        if "define" in processed_input or "what is" in processed_input or "o que" in processed_input or "definir" in processed_input:
            term = next((entity for entity in entities if entity["type"] == "term"), None)
            if term:
                definition = self.knowledge_base.get_definition(term["value"])
                if definition:
                    return definition
            
        return "Não tenho certeza de como processar esse comando. Você poderia tentar formulá-lo de outra maneira?"
    
    def _handle_conversation(self, processed_input, conversation_history):
        """Handle conversational intents"""
        # Use contextual information from conversation history
        context = self._extract_context(conversation_history)
        
        # Generate a contextually appropriate response
        return self.response_generator.generate_contextual_response(processed_input, context)
    
    def _extract_context(self, conversation_history):
        """
        Extract context from conversation history
        
        Args:
            conversation_history (list): List of previous messages
            
        Returns:
            dict: Contextual information
        """
        context = {"topics": [], "sentiment": "neutral", "last_question": None}
        
        # Only process if we have history
        if len(conversation_history) < 2:
            return context
        
        # Extract topics from the last few messages
        last_messages = conversation_history[-5:] if len(conversation_history) >= 5 else conversation_history
        
        for message in last_messages:
            if message["role"] == "user":
                # Extract topics from user messages
                topics = self.nlp_processor.extract_topics(message["content"])
                context["topics"].extend(topics)
                
                # Check if the last user message was a question
                if message == conversation_history[-2] and self.nlp_processor.is_question(message["content"]):
                    context["last_question"] = message["content"]
        
        # Remove duplicates and keep only the most recent topics
        context["topics"] = list(set(context["topics"]))[:3]
        
        return context
