"""
Ollama service for handling LLM interactions.
Manages connection, model availability, and conversation generation.
"""

import requests
import json
from typing import Optional, Generator, List, Dict
from .config import Config


class OllamaService:
    """Service class for interacting with Ollama API."""
    
    def __init__(self):
        """Initialize the Ollama service."""
        self.base_url = Config.OLLAMA_HOST
        self.model = Config.OLLAMA_MODEL
        self.timeout = Config.OLLAMA_TIMEOUT
        self.conversation_history: List[Dict[str, str]] = []
        
    def check_health(self) -> bool:
        """
        Check if Ollama server is running and accessible.
        
        Returns:
            bool: True if server is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def check_model_exists(self) -> bool:
        """
        Check if the specified model is available locally.
        
        Returns:
            bool: True if model exists, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(self.model in model.get("name", "") for model in models)
            return False
        except requests.exceptions.RequestException:
            return False
    
    def pull_model(self) -> Generator[str, None, None]:
        """
        Pull/download the specified model from Ollama.
        
        Yields:
            str: Status messages during model download
        """
        try:
            url = f"{self.base_url}/api/pull"
            data = {"name": self.model}
            
            response = requests.post(
                url, 
                json=data, 
                stream=True, 
                timeout=self.timeout
            )
            
            for line in response.iter_lines():
                if line:
                    try:
                        status = json.loads(line)
                        if "status" in status:
                            yield status["status"]
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            yield f"Error pulling model: {str(e)}"
    
    def generate_response(
        self, 
        user_message: str, 
        target_language: str = "Spanish",
        stream: bool = True
    ) -> Generator[str, None, None]:
        """
        Generate a response from Ollama for the user's message.
        
        Args:
            user_message: The user's input message
            target_language: The language the user wants to learn
            stream: Whether to stream the response
            
        Yields:
            str: Response chunks from the model
        """
        try:
            # Format the user message with language context
            formatted_message = user_message.replace("{language}", target_language)
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": formatted_message
            })
            
            # Prepare the messages for Ollama
            messages = [
                {"role": "system", "content": Config.SYSTEM_PROMPT},
                *self.conversation_history
            ]
            
            url = f"{self.base_url}/api/chat"
            data = {
                "model": self.model,
                "messages": messages,
                "stream": stream
            }
            
            response = requests.post(
                url,
                json=data,
                stream=stream,
                timeout=self.timeout
            )
            
            full_response = ""
            
            if stream:
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "message" in chunk:
                                content = chunk["message"].get("content", "")
                                full_response += content
                                yield content
                        except json.JSONDecodeError:
                            continue
            else:
                result = response.json()
                full_response = result.get("message", {}).get("content", "")
                yield full_response
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
            
        except requests.exceptions.Timeout:
            yield "⏱️ Request timed out. The model might be too slow. Try a smaller model."
        except requests.exceptions.ConnectionError:
            yield "🔌 Cannot connect to Ollama. Make sure Ollama is running with 'ollama serve'."
        except requests.exceptions.RequestException as e:
            yield f"❌ Error generating response: {str(e)}"
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def get_status_message(self) -> str:
        """
        Get a formatted status message about Ollama service.
        
        Returns:
            str: Status message with connection and model info
        """
        if not self.check_health():
            return "❌ Ollama is not running. Please start it with: `ollama serve`"
        
        if not self.check_model_exists():
            return f"⚠️ Model '{self.model}' not found. Click 'Setup Model' to download it."
        
        return f"✅ Connected to Ollama ({self.model})"
