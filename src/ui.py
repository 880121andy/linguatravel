"""
Gradio UI for LinguaTravel application.
Creates an interactive interface for language learning.
TARGET: Gradio 6.x / 4.x (Modern)
"""

import gradio as gr
import sys
from typing import List, Tuple, Optional
from .config import Config
from .ollama_service import OllamaService
from .whisper_service import WhisperService

# 🔴 DEBUG: 程式啟動時檢查版本
print(f"🔍 Runtime Gradio Version: {gr.__version__}")
if int(gr.__version__.split('.')[0]) < 4:
    print("⚠️ WARNING: You are running an old version of Gradio (<4.0)!")
    print("   Please ensure you are running the python command in the correct environment.")

class LinguaTravelUI:
    """Manages the Gradio interface for the application."""
    
    def __init__(self, ollama_service: OllamaService, whisper_service: WhisperService):
        self.ollama = ollama_service
        self.whisper = whisper_service
        self.current_language = "Spanish"
        
    def handle_text_message(
        self, 
        message: str, 
        history: List[dict]
    ) -> Tuple[str, List[dict]]:
        """Handle text message with Dictionary format (Modern)."""
        if not message.strip():
            return "", history
        
        # Gradio 4.0+ history 格式為 List[Dict]
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": ""})
        
        response = ""
        for chunk in self.ollama.generate_response(message, self.current_language):
            response += chunk
            history[-1]["content"] = response
            yield "", history
        
        return "", history
    
    def handle_audio_message(
        self,
        audio_path: Optional[str],
        history: List[dict]
    ) -> Tuple[str, List[dict]]:
        """Handle audio message."""
        if not audio_path:
            return "", history
        
        transcription = self.whisper.transcribe_audio_with_feedback(audio_path)
        history.append({"role": "assistant", "content": f"🎤 **Voice Input Detected**\n\n{transcription}"})
        
        result = self.whisper.transcribe_audio(audio_path)
        if result.get("text") and not result.get("error"):
            user_text = result["text"]
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": ""})
            
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
        """Handle quick phrase button."""
        phrase_template = Config.QUICK_PHRASES.get(phrase_key, "")
        if not phrase_template:
            return history
        
        phrase = phrase_template.replace("{language}", self.current_language)
        history.append({"role": "user", "content": phrase})
        history.append({"role": "assistant", "content": ""})
        
        response = ""
        for chunk in self.ollama.generate_response(phrase, self.current_language):
            response += chunk
            history[-1]["content"] = response
            yield history
        
        return history
    
    def update_language(self, language: str) -> str:
        self.current_language = language
        return f"🌍 Learning language changed to: **{language}**"
    
    def clear_conversation(self) -> Tuple[List, str]:
        self.ollama.clear_history()
        return [], "🗑️ Conversation cleared!"
    
    def setup_model(self) -> str:
        if self.ollama.check_model_exists():
            return f"✅ Model '{self.ollama.model}' is already available!"
        
        status_messages = []
        for status in self.ollama.pull_model():
            status_messages.append(status)
            yield "\n".join(status_messages)
        
        return "\n".join(status_messages) + "\n\n✅ Model setup complete!"
    
    def create_interface(self) -> gr.Blocks:
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
            # Gradio 6.0.1 絕對支援 type="messages"
            chatbot = gr.Chatbot(
                label="Conversation",
                height=400,
                show_label=True,
                type="messages" 
            )
            
            with gr.Row():
                with gr.Column(scale=4):
                    text_input = gr.Textbox(
                        label="Type your message",
                        placeholder="e.g., How do I say 'thank you' in Spanish?",
                        lines=1
                    )
                with gr.Column(scale=1):
                    # Gradio 6.0.1 支援 sources=["microphone"]
                    audio_input = gr.Audio(
                        sources=["microphone"], 
                        type="filepath",
                        label="🎤 Or speak"
                    )
            
            gr.Markdown("### 🚀 Quick Phrases")
            with gr.Row():
                quick_buttons = []
                for phrase_key in Config.QUICK_PHRASES.keys():
                    btn = gr.Button(phrase_key, size="sm")
                    quick_buttons.append((phrase_key, btn))
            
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
                # 移除 list()，讓 Gradio 正確處理生成器
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
