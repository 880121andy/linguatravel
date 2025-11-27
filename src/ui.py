"""
Gradio UI for LinguaTravel application.
Creates an interactive interface for language learning.
Compatible with Gradio 3.x (Legacy Mode)
"""

import gradio as gr
from typing import List, Tuple, Optional, Any
from .config import Config
from .ollama_service import OllamaService
from .whisper_service import WhisperService


class LinguaTravelUI:
    """Manages the Gradio interface for the application."""
    
    def __init__(self, ollama_service: OllamaService, whisper_service: WhisperService):
        """
        Initialize the UI with services.
        
        Args:
            ollama_service: Initialized Ollama service
            whisper_service: Initialized Whisper service
        """
        self.ollama = ollama_service
        self.whisper = whisper_service
        self.current_language = "Spanish"
        
    def handle_text_message(
        self, 
        message: str, 
        history: List[List[Any]]
    ) -> Tuple[str, List[List[Any]]]:
        """
        Handle text message from user.
        """
        if not message.strip():
            return "", history
        
        history = history or []
        
        # [Legacy] Append [User Message, Placeholder]
        history.append([message, ""])
        
        # Generate response
        response = ""
        for chunk in self.ollama.generate_response(message, self.current_language):
            response += chunk
            # Update the AI response part of the last tuple
            history[-1][1] = response
            yield "", history
        
        return "", history
    
    def handle_audio_message(
        self,
        audio_path: Optional[str],
        history: List[List[Any]]
    ) -> Tuple[str, List[List[Any]]]:
        """
        Handle audio message from user.
        """
        if not audio_path:
            return "", history
            
        history = history or []
        
        # Transcribe audio
        transcription = self.whisper.transcribe_audio_with_feedback(audio_path)
        
        # [Legacy] Use [None, Message] to show a system/status message
        history.append([None, f"🎤 **Voice Input Detected**\n\n{transcription}"])
        
        # Extract the actual text from transcription
        result = self.whisper.transcribe_audio(audio_path)
        if result.get("text") and not result.get("error"):
            user_text = result["text"]
            
            # [Legacy] Append [User Text, Placeholder]
            history.append([user_text, ""])
            
            # Generate response to the transcribed text
            response = ""
            for chunk in self.ollama.generate_response(user_text, self.current_language):
                response += chunk
                history[-1][1] = response
                yield "", history
        
        return "", history
    
    def handle_quick_phrase(
        self,
        phrase_key: str,
        history: List[List[Any]]
    ) -> List[List[Any]]:
        """
        Handle quick phrase button click.
        """
        history = history or []
        
        phrase_template = Config.QUICK_PHRASES.get(phrase_key, "")
        if not phrase_template:
            return history
        
        # Format with current language
        phrase = phrase_template.replace("{language}", self.current_language)
        
        # [Legacy] Append [User Message, Placeholder]
        history.append([phrase, ""])
        
        # Generate response
        response = ""
        for chunk in self.ollama.generate_response(phrase, self.current_language):
            response += chunk
            history[-1][1] = response
            yield history
        
        return history
    
    def update_language(self, language: str) -> str:
        """Update the target language for learning."""
        self.current_language = language
        return f"🌍 Learning language changed to: **{language}**"
    
    def clear_conversation(self) -> Tuple[List, str]:
        """Clear the conversation history."""
        self.ollama.clear_history()
        return [], "🗑️ Conversation cleared!"
    
    def setup_model(self) -> str:
        """Setup/pull the Ollama model."""
        if self.ollama.check_model_exists():
            return f"✅ Model '{self.ollama.model}' is already available!"
        
        status_messages = []
        for status in self.ollama.pull_model():
            status_messages.append(status)
            yield "\n".join(status_messages)
        
        return "\n".join(status_messages) + "\n\n✅ Model setup complete!"
    
    def create_interface(self) -> gr.Blocks:
        """Create and configure the Gradio interface."""
        with gr.Blocks(title=Config.APP_TITLE) as interface:
            
            gr.Markdown(f"# {Config.APP_TITLE}")
            gr.Markdown(Config.APP_DESCRIPTION)
            
            with gr.Row():
                with gr.Column(scale=2):
                    ollama_status = gr.Markdown(self.ollama.get_status_message())
                    whisper_status = gr.Markdown(self.whisper.get_status())
                    
                with gr.Column(scale=1):
                    language_selector = gr.Dropdown(
                        choices=Config.SUPPORTED_LANGUAGES,
                        value="Spanish",
                        label="🌍 Learning Language",
                        interactive=True
                    )
                    language_status = gr.Markdown("")
            
            # Main chat interface
            chatbot = gr.Chatbot(
                label="Conversation",
                height=400,
                show_label=True
                # 🔴 FIX: 移除了 type="messages"，因為舊版不支援
            )
            
            with gr.Row():
                with gr.Column(scale=4):
                    text_input = gr.Textbox(
                        label="Type your message",
                        placeholder="e.g., How do I say 'thank you' in Spanish?",
                        lines=1
                    )
                with gr.Column(scale=1):
                    audio_input = gr.Audio(
                        source="microphone", # 舊版可能用 source 而不是 sources
                        type="filepath",
                        label="🎤 Or speak"
                    )
            
            # Quick phrase buttons
            gr.Markdown("### 🚀 Quick Phrases")
            with gr.Row():
                quick_buttons = []
                for phrase_key in Config.QUICK_PHRASES.keys():
                    btn = gr.Button(phrase_key) # size="sm" 舊版可能不支援，先拿掉保險
                    quick_buttons.append((phrase_key, btn))
            
            # Action buttons
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear Conversation", variant="secondary")
                setup_model_btn = gr.Button("📥 Setup Model", variant="primary")
            
            setup_output = gr.Markdown("")
            
            # Event handlers
            text_input.submit(
                self.handle_text_message,
                inputs=[text_input, chatbot],
                outputs=[text_input, chatbot]
            )
            
            # 舊版 audio 處理可能略有不同，但通常 change 事件是通用的
            audio_input.change(
                self.handle_audio_message,
                inputs=[audio_input, chatbot],
                outputs=[text_input, chatbot]
            )
            
            for phrase_key, btn in quick_buttons:
                btn.click(
                    lambda history, pk=phrase_key: self.handle_quick_phrase(pk, history),
                    inputs=[chatbot],
                    outputs=[chatbot]
                )
            
            language_selector.change(
                self.update_language,
                inputs=[language_selector],
                outputs=[language_status]
            )
            
            clear_btn.click(
                self.clear_conversation,
                outputs=[chatbot, language_status]
            )
            
            setup_model_btn.click(
                self.setup_model,
                outputs=[setup_output]
            )
            
            gr.Markdown("""
            ---
            **Tips:**
            - 💬 Type or speak to practice conversations
            - 🎯 Use quick phrases for common scenarios
            - 🎤 Use voice input to practice pronunciation
            - 🌍 Switch languages to learn different phrases
            """)
        
        return interface
