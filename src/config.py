"""
Configuration management for LinguaTravel application.
Handles all settings for Ollama, Whisper, and Gradio components.
"""

import os
from typing import Dict, List

class Config:
    """Central configuration class for the application."""
    
    # Ollama Configuration
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma2:2b")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    
    # Whisper Configuration
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "auto")  # auto, cuda, cpu
    
    # Gradio UI Configuration
    GRADIO_PORT: int = int(os.getenv("GRADIO_PORT", "7860"))
    GRADIO_SHARE: bool = os.getenv("GRADIO_SHARE", "False").lower() == "true"
    GRADIO_THEME: str = os.getenv("GRADIO_THEME", "default")
    
    # Application Configuration
    APP_TITLE: str = "🌍 LinguaTravel - Your Travel Language Assistant"
    APP_DESCRIPTION: str = """
    Practice common travel phrases, get translations, and improve your pronunciation!
    Perfect for travelers who want to communicate confidently in a new country.
    """
    
    # Supported Languages for Learning
    SUPPORTED_LANGUAGES: List[str] = [
        "Spanish",
        "French", 
        "German",
        "Italian",
        "Japanese",
        "Chinese (Mandarin)",
        "Korean",
        "Portuguese",
        "Arabic",
        "Russian"
    ]
    
    # Travel Scenarios
    QUICK_PHRASES: Dict[str, str] = {
        "🙋 Greetings": "Teach me how to greet people politely in {language}",
        "🗺️ Directions": "How do I ask for directions in {language}?",
        "🍽️ Ordering Food": "Help me order food at a restaurant in {language}",
        "🚨 Emergency": "What are essential emergency phrases in {language}?",
        "🏨 Hotel": "Teach me useful phrases for checking into a hotel in {language}",
        "🛒 Shopping": "How do I ask about prices and bargain in {language}?"
    }
    
    # System Prompt Template for Ollama
    SYSTEM_PROMPT: str = """You are LinguaTravel, a friendly and knowledgeable language learning assistant for travelers.

Your role is to:
1. Help users learn practical phrases for travel situations
2. Provide accurate translations with pronunciation guides
3. Explain cultural context when relevant
4. Keep responses concise and practical (2-4 sentences max)
5. Use phonetic pronunciation in parentheses when showing phrases
6. Encourage practice and provide positive feedback

Always be encouraging, patient, and focus on practical communication skills that travelers need.
"""

    @classmethod
    def get_whisper_device(cls) -> str:
        """
        Determine the best device for Whisper model.
        
        Returns:
            str: Device name ('cuda' or 'cpu')
        """
        if cls.WHISPER_DEVICE == "auto":
            try:
                import torch
                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return cls.WHISPER_DEVICE
    
    @classmethod
    def validate_config(cls) -> tuple[bool, str]:
        """
        Validate configuration settings.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not cls.OLLAMA_HOST:
            return False, "OLLAMA_HOST cannot be empty"
        
        if not cls.OLLAMA_MODEL:
            return False, "OLLAMA_MODEL cannot be empty"
        
        if not cls.WHISPER_MODEL:
            return False, "WHISPER_MODEL cannot be empty"
        
        return True, ""
