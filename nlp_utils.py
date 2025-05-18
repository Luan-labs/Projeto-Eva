import re
import logging
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np

logger = logging.getLogger(__name__)

class NLPProcessor:
    """
    Utility class for natural language processing tasks
    """
    
    def __init__(self):
        """Initialize NLP processor and download necessary NLTK resources"""
        try:
            # Download NLTK resources
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
            
            # Initialize components
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
            
            # Initialize intent classifier
            self._init_intent_classifier()
            
            logger.info("NLP processor initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing NLP processor: {str(e)}")
    
    def _init_intent_classifier(self):
        """Initialize the intent classifier with training data"""
        # Sample data for intent classification (English and Portuguese)
        self.intent_data = {
            "greeting": [
                "hello", "hi", "hey", "greetings", "good morning", 
                "good afternoon", "good evening", "howdy", "what's up",
                "hi there", "hello there", "hey there",
                "olá", "oi", "e aí", "saudações", "bom dia",
                "boa tarde", "boa noite", "tudo bem", "como vai",
                "oi tudo bem", "olá tudo bem", "e aí tudo bem"
            ],
            "farewell": [
                "goodbye", "bye", "see you", "farewell", "see you later",
                "good night", "have a nice day", "take care", "until next time",
                "bye bye", "so long", "catch you later",
                "adeus", "tchau", "até logo", "até mais", "nos vemos depois",
                "boa noite", "tenha um bom dia", "cuide-se", "até a próxima",
                "tchau tchau", "até mais tarde", "até breve"
            ],
            "question": [
                "what is", "how do", "why is", "where is", "when did",
                "can you explain", "tell me about", "who is", "could you tell me",
                "I need information on", "explain", "define", "describe",
                "o que é", "como", "por que", "onde está", "quando",
                "pode explicar", "me fale sobre", "quem é", "poderia me dizer",
                "preciso de informações sobre", "explique", "defina", "descreva"
            ],
            "command": [
                "show me", "tell me", "find", "search for", "give me",
                "I want to know", "look up", "calculate", "compute",
                "solve", "help me with", "assist me",
                "mostre", "diga-me", "encontre", "procure por", "me dê",
                "quero saber", "procure", "calcule", "compute",
                "resolva", "me ajude com", "me assista"
            ],
            "conversation": [
                "I feel", "I think", "in my opinion", "do you agree",
                "what do you think", "let's talk about", "I believe",
                "I'd like to discuss", "let's discuss", "I want to talk about",
                "eu sinto", "eu acho", "na minha opinião", "você concorda",
                "o que você acha", "vamos falar sobre", "eu acredito",
                "eu gostaria de discutir", "vamos discutir", "quero falar sobre"
            ]
        }
        
        # Prepare training data
        X_train = []
        y_train = []
        
        for intent, phrases in self.intent_data.items():
            for phrase in phrases:
                X_train.append(phrase)
                y_train.append(intent)
        
        # Create a classifier
        self.vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 2))
        X_train_vec = self.vectorizer.fit_transform(X_train)
        
        self.intent_classifier = MultinomialNB()
        self.intent_classifier.fit(X_train_vec, y_train)
        
        logger.info("Intent classifier trained successfully")
    
    def preprocess_text(self, text):
        """
        Preprocess text for NLP tasks
        
        Args:
            text (str): Input text
            
        Returns:
            str: Preprocessed text
        """
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove punctuation
            text = text.translate(str.maketrans('', '', string.punctuation))
            
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stop words
            tokens = [token for token in tokens if token not in self.stop_words]
            
            # Lemmatize
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
            # Rejoin tokens
            return ' '.join(tokens)
        
        except Exception as e:
            logger.error(f"Error preprocessing text: {str(e)}")
            return text
    
    def classify_intent(self, text):
        """
        Classify the intent of the text
        
        Args:
            text (str): Input text
            
        Returns:
            str: Classified intent
        """
        try:
            # Convert text to vector
            text_vec = self.vectorizer.transform([text])
            
            # Predict intent
            intent = self.intent_classifier.predict(text_vec)[0]
            
            # Rule-based refinements for better accuracy
            if '?' in text:
                intent = "question"
            elif any(greeting in text for greeting in ["hello", "hi ", "hey ", "morning", "afternoon", "evening"]):
                intent = "greeting"
            elif any(farewell in text for farewell in ["bye", "goodbye", "see you", "later"]):
                intent = "farewell"
            
            return intent
        
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return "conversation"  # Default to conversation
    
    def extract_entities(self, text):
        """
        Extract named entities and other important elements from text
        
        Args:
            text (str): Input text
            
        Returns:
            list: Extracted entities with type and value
        """
        try:
            entities = []
            
            # Extract terms after "what is" or "define" (English)
            what_is_match = re.search(r"what\s+is\s+(?:a|an)?\s*([a-z0-9 ]+)", text)
            define_match = re.search(r"define\s+(?:a|an)?\s*([a-z0-9 ]+)", text)
            
            # Extract terms after "o que é" or "defina" (Portuguese)
            o_que_match = re.search(r"o\s+que\s+(?:é|e|eh)\s+(?:um|uma)?\s*([a-z0-9 ]+)", text.lower())
            defina_match = re.search(r"defin(?:a|e|ir)\s+(?:um|uma)?\s*([a-z0-9 ]+)", text.lower())
            
            if what_is_match:
                entities.append({
                    "type": "term",
                    "value": what_is_match.group(1).strip()
                })
            elif define_match:
                entities.append({
                    "type": "term",
                    "value": define_match.group(1).strip()
                })
            elif o_que_match:
                entities.append({
                    "type": "term",
                    "value": o_que_match.group(1).strip()
                })
            elif defina_match:
                entities.append({
                    "type": "term",
                    "value": defina_match.group(1).strip()
                })
            
            # Extract dates (both formats DD/MM/YYYY and MM/DD/YYYY)
            date_matches = re.findall(r"\b\d{1,2}\/\d{1,2}\/\d{2,4}\b", text)
            for date in date_matches:
                entities.append({
                    "type": "date",
                    "value": date
                })
            
            # Extract numbers
            number_matches = re.findall(r"\b\d+(?:\.\d+)?\b", text)
            for number in number_matches:
                entities.append({
                    "type": "number",
                    "value": float(number)
                })
            
            return entities
        
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return []
    
    def extract_topics(self, text):
        """
        Extract main topics from text
        
        Args:
            text (str): Input text
            
        Returns:
            list: Extracted topics
        """
        try:
            # Tokenize and remove stopwords
            tokens = word_tokenize(text.lower())
            tokens = [token for token in tokens if token not in self.stop_words and token.isalpha()]
            
            # Count occurrences
            word_counts = {}
            for token in tokens:
                word_counts[token] = word_counts.get(token, 0) + 1
            
            # Sort by count and return top topics
            sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            topics = [word for word, count in sorted_words[:3]]
            
            return topics
        
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            return []
    
    def is_question(self, text):
        """
        Determine if the text is a question
        
        Args:
            text (str): Input text
            
        Returns:
            bool: True if the text is a question, False otherwise
        """
        # Check for question mark
        if '?' in text:
            return True
        
        # Check for question words at the beginning (English and Portuguese)
        question_starters = [
            # English
            'what', 'who', 'where', 'when', 'why', 'how', 'can', 'could', 'would', 'should', 'is', 'are', 'does', 'do',
            # Portuguese
            'o que', 'quem', 'onde', 'quando', 'por que', 'como', 'pode', 'poderia', 'seria', 'deveria', 'é', 'são', 'faz', 'fazem'
        ]
        
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        if words and words[0] in question_starters:
            return True
        
        # Check for Portuguese two-word question starters
        for starter in question_starters:
            if ' ' in starter and text_lower.startswith(starter):
                return True
        
        return False
