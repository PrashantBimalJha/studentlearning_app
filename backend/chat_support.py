"""
🎓 Learning App - AI Chat Support System
AI-powered tuition teacher using Ollama to help students with their questions
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os

# Load environment variables from YAML file
from utils import load_env_from_yaml
load_env_from_yaml()

# LangChain imports
try:
    from langchain_community.llms import Ollama
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationChain
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langsmith import Client
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Setup logger
logger = logging.getLogger(__name__)

class AITuitionTeacher:
    """
    AI-powered tuition teacher using Ollama to provide educational support
    """
    
    def __init__(self, ollama_base_url: str = None):
        """
        Initialize the AI Tuition Teacher
        
        Args:
            ollama_base_url: Base URL for Ollama API (default: from environment)
        """
        self.ollama_base_url = ollama_base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.conversation_history = {}  # Store conversation history per user
        
        # Initialize LangSmith if available
        self.langsmith_client = None
        if LANGCHAIN_AVAILABLE:
            try:
                # Set up LangSmith using environment variables
                langchain_api_key = os.getenv('LANGCHAIN_API_KEY')
                langchain_project = os.getenv('LANGCHAIN_PROJECT', 'learning-app-ai')
                langchain_endpoint = os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
                langchain_tracing = os.getenv('LANGCHAIN_TRACING_V2', 'true')
                
                if langchain_api_key and langchain_api_key != "YOUR_LANGCHAIN_API_KEY_HERE":
                    os.environ["LANGCHAIN_TRACING_V2"] = langchain_tracing
                    os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
                    os.environ["LANGCHAIN_PROJECT"] = langchain_project
                    os.environ["LANGCHAIN_ENDPOINT"] = langchain_endpoint
                    
                    self.langsmith_client = Client()
                    logger.info("LangSmith client initialized successfully")
                else:
                    logger.warning("LANGCHAIN_API_KEY not found or is placeholder. Please set a valid API key in your environment variables.")
            except Exception as e:
                logger.warning(f"Failed to initialize LangSmith: {e}")
                self.langsmith_client = None
        
        # Initialize LangChain Ollama if available
        self.llm = None
        if LANGCHAIN_AVAILABLE:
            try:
                self.llm = Ollama(
                    base_url=self.ollama_base_url,
                    model=self.model_name,
                    temperature=0.7
                )
                logger.info(f"LangChain Ollama initialized with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize LangChain Ollama: {e}")
                self.llm = None
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt that defines the AI teacher's role and behavior
        """
        return """You are an experienced and friendly AI tuition teacher for the Learning App. Your role is to help students with their academic questions and provide educational support.

PERSONALITY & APPROACH:
- Be encouraging, patient, and supportive
- Use a warm, friendly tone that motivates students
- Break down complex topics into simple, understandable parts
- Ask clarifying questions when needed
- Provide examples and analogies to help understanding
- Celebrate student progress and effort

TEACHING STYLE:
- Start with the basics and build up complexity
- Use step-by-step explanations
- Provide multiple examples for better understanding
- Encourage critical thinking and problem-solving
- Suggest related topics for deeper learning
- Use emojis appropriately to make learning fun

SUBJECTS YOU CAN HELP WITH:
- Mathematics (algebra, geometry, calculus, statistics)
- Science (physics, chemistry, biology, earth science)
- English (grammar, literature, writing, comprehension)
- History and Social Studies
- Computer Science and Programming
- Study techniques and exam preparation
- General academic guidance

RESPONSE FORMAT:
- Keep responses concise but comprehensive
- Use bullet points or numbered lists when helpful
- Include relevant examples
- End with encouraging words or next steps
- Use markdown formatting for better readability

Remember: Your goal is to make learning enjoyable and accessible for every student!"""

    def _check_ollama_connection(self) -> bool:
        """
        Check if Ollama is running and accessible
        
        Returns:
            bool: True if Ollama is accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return False

    def _get_available_models(self) -> List[str]:
        """
        Get list of available Ollama models
        
        Returns:
            List[str]: List of available model names
        """
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []

    def _ensure_model_available(self) -> bool:
        """
        Ensure the required model is available, pull if necessary
        
        Returns:
            bool: True if model is available, False otherwise
        """
        try:
            # Check if model exists
            models = self._get_available_models()
            if self.model_name in models:
                return True
            
            # Try to pull the model
            logger.info(f"Model {self.model_name} not found. Attempting to pull...")
            pull_response = requests.post(
                f"{self.ollama_base_url}/api/pull",
                json={"name": self.model_name},
                timeout=300  # 5 minutes timeout for model pull
            )
            
            if pull_response.status_code == 200:
                logger.info(f"Successfully pulled model {self.model_name}")
                return True
            else:
                logger.error(f"Failed to pull model {self.model_name}: {pull_response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error ensuring model availability: {e}")
            return False

    def _get_conversation_context(self, user_id: str, max_messages: int = 10) -> str:
        """
        Get conversation context for the user
        
        Args:
            user_id: User ID
            max_messages: Maximum number of previous messages to include
            
        Returns:
            str: Formatted conversation context
        """
        if user_id not in self.conversation_history:
            return ""
        
        history = self.conversation_history[user_id][-max_messages:]
        context = ""
        
        for msg in history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                context += f"Student: {content}\n"
            else:
                context += f"Teacher: {content}\n"
        
        return context

    def _add_to_conversation_history(self, user_id: str, role: str, content: str):
        """
        Add message to conversation history
        
        Args:
            user_id: User ID
            role: 'user' or 'assistant'
            content: Message content
        """
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 20 messages to prevent memory issues
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]

    def _generate_response(self, user_question: str, user_id: str) -> str:
        """
        Generate AI response using Ollama
        
        Args:
            user_question: Student's question
            user_id: User ID for conversation context
            
        Returns:
            str: AI teacher's response
        """
        try:
            # Get conversation context
            context = self._get_conversation_context(user_id)
            
            # Prepare the prompt
            prompt = f"{self.system_prompt}\n\n"
            if context:
                prompt += f"Previous conversation:\n{context}\n\n"
            prompt += f"Student's current question: {user_question}\n\nPlease provide a helpful and encouraging response:"
            
            # Prepare request data
            request_data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            # Make request to Ollama
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', 'I apologize, but I could not generate a response at this time.')
                
                # Add to conversation history
                self._add_to_conversation_history(user_id, 'user', user_question)
                self._add_to_conversation_history(user_id, 'assistant', ai_response)
                
                return ai_response
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return "I'm sorry, I'm having trouble connecting to my AI system right now. Please try again later."
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "I'm taking a bit longer to think about your question. Please try again in a moment."
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I apologize, but I encountered an error while processing your question. Please try again."

    def chat_with_student(self, user_id: str, question: str) -> Dict[str, any]:
        """
        Main method to chat with a student
        
        Args:
            user_id: User ID
            question: Student's question
            
        Returns:
            Dict containing response and metadata
        """
        try:
            # Check Ollama connection
            if not self._check_ollama_connection():
                return {
                    "success": False,
                    "response": "I'm sorry, my AI system is currently unavailable. Please make sure Ollama is running and try again later.",
                    "error": "Ollama connection failed"
                }
            
            # Ensure model is available
            if not self._ensure_model_available():
                return {
                    "success": False,
                    "response": "I'm sorry, I'm having trouble accessing my AI model. Please try again later.",
                    "error": "Model not available"
                }
            
            # Generate response
            ai_response = self._generate_response(question, user_id)
            
            return {
                "success": True,
                "response": ai_response,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error in chat_with_student: {e}")
            return {
                "success": False,
                "response": "I apologize, but I encountered an unexpected error. Please try again later.",
                "error": str(e)
            }

    def clear_conversation_history(self, user_id: str) -> bool:
        """
        Clear conversation history for a user
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if cleared successfully
        """
        try:
            if user_id in self.conversation_history:
                del self.conversation_history[user_id]
            return True
        except Exception as e:
            logger.error(f"Error clearing conversation history: {e}")
            return False

    def get_conversation_summary(self, user_id: str) -> Dict[str, any]:
        """
        Get summary of conversation with a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dict containing conversation summary
        """
        if user_id not in self.conversation_history:
            return {
                "user_id": user_id,
                "message_count": 0,
                "last_message": None,
                "conversation": []
            }
        
        history = self.conversation_history[user_id]
        return {
            "user_id": user_id,
            "message_count": len(history),
            "last_message": history[-1] if history else None,
            "conversation": history
        }

    def change_model(self, new_model: str) -> bool:
        """
        Change the AI model being used
        
        Args:
            new_model: Name of the new model
            
        Returns:
            bool: True if model changed successfully
        """
        try:
            models = self._get_available_models()
            if new_model in models:
                self.model_name = new_model
                logger.info(f"Model changed to {new_model}")
                return True
            else:
                logger.error(f"Model {new_model} not available")
                return False
        except Exception as e:
            logger.error(f"Error changing model: {e}")
            return False

    def get_system_status(self) -> Dict[str, any]:
        """
        Get system status and available models
        
        Returns:
            Dict containing system status
        """
        try:
            ollama_connected = self._check_ollama_connection()
            available_models = self._get_available_models() if ollama_connected else []
            
            return {
                "ollama_connected": ollama_connected,
                "current_model": self.model_name,
                "available_models": available_models,
                "active_conversations": len(self.conversation_history),
                "total_messages": sum(len(history) for history in self.conversation_history.values())
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "ollama_connected": False,
                "current_model": self.model_name,
                "available_models": [],
                "active_conversations": 0,
                "total_messages": 0,
                "error": str(e)
            }


# Global instance
ai_teacher = AITuitionTeacher()

# Convenience functions for easy import
def chat_with_ai_teacher(user_id: str, question: str) -> Dict[str, any]:
    """Convenience function to chat with AI teacher"""
    return ai_teacher.chat_with_student(user_id, question)

def clear_ai_conversation(user_id: str) -> bool:
    """Convenience function to clear AI conversation"""
    return ai_teacher.clear_conversation_history(user_id)

def get_ai_system_status() -> Dict[str, any]:
    """Convenience function to get AI system status"""
    return ai_teacher.get_system_status()
