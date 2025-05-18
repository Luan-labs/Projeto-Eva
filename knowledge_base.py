import json
import os
import logging
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """
    Simple knowledge base that stores information and provides
    search capabilities using TF-IDF and cosine similarity
    """
    
    def __init__(self, knowledge_file="data/knowledge.json"):
        """
        Initialize the knowledge base from a JSON file
        
        Args:
            knowledge_file (str): Path to the JSON file containing knowledge
        """
        self.knowledge = []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.knowledge_vectors = None
        
        # Load knowledge from JSON file
        self._load_knowledge(knowledge_file)
        
        # Create vector representations of knowledge
        self._vectorize_knowledge()
    
    def _load_knowledge(self, knowledge_file):
        """
        Load knowledge from a JSON file
        
        Args:
            knowledge_file (str): Path to the JSON file containing knowledge
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(knowledge_file), exist_ok=True)
            
            # Check if file exists, if not create it with initial data
            if not os.path.exists(knowledge_file):
                self._create_initial_knowledge(knowledge_file)
            
            # Load the knowledge from file
            with open(knowledge_file, 'r') as f:
                self.knowledge = json.load(f)
                
            logger.info(f"Loaded {len(self.knowledge)} knowledge entries")
        
        except Exception as e:
            logger.error(f"Error loading knowledge: {str(e)}")
            # Initialize with some basic knowledge if file loading fails
            self._initialize_basic_knowledge()
    
    def _create_initial_knowledge(self, knowledge_file):
        """
        Create initial knowledge file with basic information
        
        Args:
            knowledge_file (str): Path where the JSON file will be created
        """
        initial_knowledge = self._get_initial_knowledge()
        
        try:
            with open(knowledge_file, 'w') as f:
                json.dump(initial_knowledge, f, indent=2)
            logger.info(f"Created initial knowledge file at {knowledge_file}")
        except Exception as e:
            logger.error(f"Error creating initial knowledge file: {str(e)}")
    
    def _initialize_basic_knowledge(self):
        """Initialize with basic knowledge if file loading fails"""
        self.knowledge = self._get_initial_knowledge()
        logger.info("Initialized with basic knowledge")
    
    def _get_initial_knowledge(self):
        """
        Get initial knowledge entries
        
        Returns:
            list: Initial knowledge entries
        """
        return [
            {
                "question": "What is artificial intelligence?",
                "answer": "Artificial intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. The term also refers to machines that mimic cognitive functions such as learning and problem-solving.",
                "category": "technology"
            },
            {
                "question": "How does machine learning work?",
                "answer": "Machine learning is a subset of AI that allows systems to learn and improve from experience without being explicitly programmed. It works by identifying patterns in data and making decisions with minimal human intervention.",
                "category": "technology"
            },
            {
                "question": "What is the difference between AI and machine learning?",
                "answer": "Artificial Intelligence is a broader concept where machines simulate human intelligence, while Machine Learning is a subset of AI that focuses on training algorithms to learn patterns from data and make predictions or decisions.",
                "category": "technology"
            },
            {
                "question": "What are neural networks?",
                "answer": "Neural networks are computing systems inspired by the human brain's biological neurons. They consist of layers of interconnected nodes or 'neurons' that process information and learn to recognize patterns in data.",
                "category": "technology"
            },
            {
                "question": "Who are you?",
                "answer": "I am a self-contained AI assistant designed to have basic conversational abilities, knowledge retrieval, and decision-making capabilities without requiring external API dependencies.",
                "category": "identity"
            },
            {
                "question": "What can you do?",
                "answer": "I can have basic conversations, answer questions based on my internal knowledge, make simple decisions, and maintain context within our conversation.",
                "category": "capabilities"
            },
            {
                "question": "What is the capital of France?",
                "answer": "The capital of France is Paris.",
                "category": "geography"
            },
            {
                "question": "How do computers store data?",
                "answer": "Computers store data in binary form, using bits (0s and 1s). These bits are physically stored in various media like hard drives (using magnetic storage), solid-state drives (using flash memory), optical discs, and RAM for temporary storage.",
                "category": "technology"
            },
            {
                "question": "What is the water cycle?",
                "answer": "The water cycle, also known as the hydrologic cycle, is the continuous movement of water on, above, and below the Earth's surface. It involves processes like evaporation, condensation, precipitation, infiltration, and runoff.",
                "category": "science"
            },
            {
                "question": "What is photosynthesis?",
                "answer": "Photosynthesis is the process by which green plants, algae, and some bacteria convert light energy, usually from the sun, into chemical energy in the form of glucose or other carbohydrates.",
                "category": "science"
            }
        ]
    
    def _vectorize_knowledge(self):
        """Create vector representations of knowledge for efficient searching"""
        try:
            # Extract text from knowledge entries
            knowledge_texts = [f"{entry['question']} {entry['answer']}" for entry in self.knowledge]
            
            # Create TF-IDF vectors
            self.knowledge_vectors = self.vectorizer.fit_transform(knowledge_texts)
            logger.info("Knowledge vectorization complete")
        
        except Exception as e:
            logger.error(f"Error vectorizing knowledge: {str(e)}")
    
    def search(self, query, threshold=0.3):
        """
        Search the knowledge base for relevant information
        
        Args:
            query (str): The search query
            threshold (float): Similarity threshold (0-1)
            
        Returns:
            list: Relevant knowledge entries
        """
        try:
            # Transform query to vector representation
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarity with all knowledge entries
            similarities = cosine_similarity(query_vector, self.knowledge_vectors).flatten()
            
            # Get indices of entries exceeding the threshold
            relevant_indices = np.where(similarities > threshold)[0]
            
            # Sort by similarity (highest first)
            relevant_indices = sorted(relevant_indices, key=lambda idx: similarities[idx], reverse=True)
            
            # Return relevant entries
            results = [self.knowledge[idx] for idx in relevant_indices]
            
            logger.debug(f"Found {len(results)} relevant entries for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    def get_definition(self, term):
        """
        Get definition for a specific term
        
        Args:
            term (str): The term to define
            
        Returns:
            str: Definition or None if not found
        """
        # Search for the term in our knowledge base
        results = self.search(f"what is {term}")
        
        if results:
            return results[0]["answer"]
        
        return None
    
    def get_random_fact(self, category=None):
        """
        Get a random fact, optionally filtered by category
        
        Args:
            category (str, optional): Category to filter by
            
        Returns:
            dict: Random knowledge entry
        """
        if category:
            filtered_knowledge = [entry for entry in self.knowledge if entry.get("category") == category]
            if filtered_knowledge:
                return random.choice(filtered_knowledge)
        
        # Return random entry if no category specified or no entries found for category
        return random.choice(self.knowledge) if self.knowledge else None
