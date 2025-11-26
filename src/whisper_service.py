"""
Whisper service for speech-to-text functionality.
Handles audio transcription for pronunciation practice.
"""

import whisper
import os
import tempfile
from typing import Optional, Dict
from .config import Config


class WhisperService:
    """Service class for Whisper speech recognition."""
    
    def __init__(self):
        """Initialize the Whisper service."""
        self.model = None
        self.model_name = Config.WHISPER_MODEL
        self.device = Config.get_whisper_device()
        self.is_loaded = False
        
    def load_model(self) -> tuple[bool, str]:
        """
        Load the Whisper model.
        
        Returns:
            tuple: (success, message)
        """
        try:
            print(f"Loading Whisper model '{self.model_name}' on {self.device}...")
            self.model = whisper.load_model(
                self.model_name,
                device=self.device
            )
            self.is_loaded = True
            return True, f"✅ Whisper model loaded successfully on {self.device}"
        except Exception as e:
            self.is_loaded = False
            return False, f"❌ Failed to load Whisper model: {str(e)}"
    
    def transcribe_audio(
        self, 
        audio_path: str, 
        language: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file
            language: Optional language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            dict: Contains 'text' (transcription) and 'language' (detected/specified)
        """
        if not self.is_loaded:
            success, message = self.load_model()
            if not success:
                return {
                    "text": "",
                    "language": "",
                    "error": message
                }
        
        try:
            # Check if file exists and is not empty
            if not os.path.exists(audio_path):
                return {
                    "text": "",
                    "language": "",
                    "error": "Audio file not found"
                }
            
            if os.path.getsize(audio_path) == 0:
                return {
                    "text": "",
                    "language": "",
                    "error": "Audio file is empty. Please record again."
                }
            
            # Transcribe the audio
            options = {}
            if language:
                options["language"] = language
            
            result = self.model.transcribe(audio_path, **options)
            
            return {
                "text": result.get("text", "").strip(),
                "language": result.get("language", "unknown"),
                "error": None
            }
            
        except Exception as e:
            return {
                "text": "",
                "language": "",
                "error": f"Transcription failed: {str(e)}"
            }
    
    def transcribe_audio_with_feedback(
        self,
        audio_path: str,
        expected_language: Optional[str] = None
    ) -> str:
        """
        Transcribe audio and provide user-friendly feedback.
        
        Args:
            audio_path: Path to the audio file
            expected_language: Expected language code
            
        Returns:
            str: Formatted transcription result with feedback
        """
        result = self.transcribe_audio(audio_path, expected_language)
        
        if result.get("error"):
            return f"❌ {result['error']}"
        
        if not result.get("text"):
            return "🎤 No speech detected. Please try again and speak clearly."
        
        detected_lang = result.get("language", "unknown")
        text = result.get("text")
        
        feedback = f"📝 **Transcription:** {text}\n"
        feedback += f"🌐 **Detected Language:** {detected_lang.upper()}"
        
        return feedback
    
    def get_status(self) -> str:
        """
        Get the current status of the Whisper service.
        
        Returns:
            str: Status message
        """
        if self.is_loaded:
            return f"✅ Whisper ready ({self.model_name} on {self.device})"
        else:
            return "⏳ Whisper model not loaded yet"
