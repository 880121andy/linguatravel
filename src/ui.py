"""
Gradio UI for LinguaTravel application.
Creates an interactive interface for language learning.
"""

import gradio as gr
from typing import List, Tuple, Optional
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
        history: List[dict]
    ) -> Tuple[str, List[dict]]:
        """
        Handle text message from user.
        
        Args:
            message: User's text message
            history: Chat history (list of dicts with 'role' and 'content')
            
        Returns:
            tuple: (empty string for clearing input, updated history)
        """
        if not message.strip():
            return "", history
        
        # Add user message to history
        history.append({"role": "user", "content": message})
        
        # Add assistant message placeholder
        history.append({"role": "assistant", "content": ""})
        
        # Generate response
        response = ""
        for chunk in self.ollama.generate_response(message, self.current_language):
            response += chunk
            # Update the last message in history with streaming response
            history[-1]["content"] = response
            yield "", history
        
        return "", history
    
    def handle_audio_message(
        self,
        audio_path: Optional[str],
        history: List[dict]
    ) -> Tuple[str, List[dict]]:
        """
        Handle audio message from user.
        
        Args:
            audio_path: Path to recorded audio file
            history: Chat history (list of dicts with 'role' and 'content')
            
        Returns:
            tuple: (empty string, updated history)
        """
        if not audio_path:
            return "", history
        
        # Transcribe audio
        transcription = self.whisper.transcribe_audio_with_feedback(audio_path)
        
        # Add transcription feedback to history
        history.append({"role": "assistant", "content": f"🎤 **Voice Input Detected**\n\n{transcription}"})
        
        # Extract the actual text from transcription
        result = self.whisper.transcribe_audio(audio_path)
        if result.get("text") and not result.get("error"):
            user_text = result["text"]
            
            # Add user's transcribed message
            history.append({"role": "user", "content": user_text})
            
            # Add assistant message placeholder
            history.append({"role": "assistant", "content": ""})
            
            # Generate response to the transcribed text
            response = ""
            for chunk in self.ollama.generate_response(user_text, self.current_language):
                response += chunk
                history[-1]["content"] = response
                yield "", history
        
        return "", history
    
    def handle_quick_phrase(
        self,
        phrase_key: str,
        history: List[dict]
    ) -> List[dict]:
        """
        Handle quick phrase button click.
        
        Args:
            phrase_key: The key of the quick phrase
            history: Chat history (list of dicts with 'role' and 'content')
            
        Returns:
            list: Updated history
        """
        phrase_template = Config.QUICK_PHRASES.get(phrase_key, "")
        if not phrase_template:
            return history
        
        # Format with current language
        phrase = phrase_template.replace("{language}", self.current_language)
        
        # Add user message to history
        history.append({"role": "user", "content": phrase})
        
        # Add assistant message placeholder
        history.append({"role": "assistant", "content": ""})
        
        # Generate response
        response = ""
        for chunk in self.ollama.generate_response(phrase, self.current_language):
            response += chunk
            history[-1]["content"] = response
            yield history
        
        return history
    
    def update_language(self, language: str) -> str:
        """
        Update the target language for learning.
        
        Args:
            language: New target language
            
        Returns:
            str: Confirmation message
        """
        self.current_language = language
        return f"🌍 Learning language changed to: **{language}**"
    
    def clear_conversation(self) -> Tuple[List, str]:
        """
        Clear the conversation history.
        
        Returns:
            tuple: (empty history, status message)
        """
        self.ollama.clear_history()
        return [], "🗑️ Conversation cleared!"
    
    def setup_model(self) -> str:
        """
        Setup/pull the Ollama model.
        
        Returns:
            str: Status message
        """
        if self.ollama.check_model_exists():
            return f"✅ Model '{self.ollama.model}' is already available!"
        
        status_messages = []
        for status in self.ollama.pull_model():
            status_messages.append(status)
            yield "\n".join(status_messages)
        
        return "\n".join(status_messages) + "\n\n✅ Model setup complete!"
    
    def create_interface(self) -> gr.Blocks:
        """
        Create and configure the Gradio interface.
        
        Returns:
            gr.Blocks: Configured Gradio interface
        """
        with gr.Blocks(
            title=Config.APP_TITLE
        ) as interface:
            
            gr.Markdown(f"# {Config.APP_TITLE}")
            gr.Markdown(Config.APP_DESCRIPTION)
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Status indicators
                    ollama_status = gr.Markdown(
                        self.ollama.get_status_message()
                    )
                    whisper_status = gr.Markdown(
                        self.whisper.get_status()
                    )
                    
                with gr.Column(scale=1):
                    # Language selector
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
                show_label=True,
                type="messages"  # 這裡指定了 messages 格式，解決格式錯誤問題
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
                        sources=["microphone"],
                        type="filepath",
                        label="🎤 Or speak"
                    )
            
            # Quick phrase buttons
            gr.Markdown("### 🚀 Quick Phrases")
            with gr.Row():
                quick_buttons = []
                for phrase_key in Config.QUICK_PHRASES.keys():
                    btn = gr.Button(phrase_key, size="sm")
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
            
            audio_input.change(
                self.handle_audio_message,
                inputs=[audio_input, chatbot],
                outputs=[text_input, chatbot]
            )
            
            for phrase_key, btn in quick_buttons:
                # 這裡移除了 list()，修正了生成器被破壞的問題
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
            
            # Footer
            gr.Markdown("""
            ---
            **Tips:**
            - 💬 Type or speak to practice conversations
            - 🎯 Use quick phrases for common scenarios
            - 🎤 Use voice input to practice pronunciation
            - 🌍 Switch languages to learn different phrases
            """)
        
        return interface
