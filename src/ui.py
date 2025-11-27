"""
Gradio UI for LinguaTravel application.
Universal Compatibility Mode
"""

import gradio as gr
from typing import List, Tuple, Optional, Any
from .config import Config
from .ollama_service import OllamaService
from .whisper_service import WhisperService

class LinguaTravelUI:
    """Manages the Gradio interface for the application."""
    
    def __init__(self, ollama_service: OllamaService, whisper_service: WhisperService):
        self.ollama = ollama_service
        self.whisper = whisper_service
        self.current_language = "Spanish"
        
    def handle_text_message(
        self, 
        message: str, 
        history: List[List[Any]]
    ) -> Tuple[str, List[List[Any]]]:
        """
        Handle text message using List of Lists format (Universal compatibility).
        """
        if not message.strip():
            return "", history
        
        history = history or []
        
        # 1. 使用 [User, None] 格式加入使用者訊息
        # 注意：這裡用列表 [message, ""] 代表一組對話
        history.append([message, ""])
        
        response = ""
        # 串流生成回應
        for chunk in self.ollama.generate_response(message, self.current_language):
            response += chunk
            # 更新最後一組對話的第二個元素 (AI 回應)
            history[-1][1] = response
            yield "", history
        
        return "", history
    
    def handle_audio_message(
        self,
        audio_path: Optional[str],
        history: List[List[Any]]
    ) -> Tuple[str, List[List[Any]]]:
        """
        Handle audio message using List of Lists format.
        """
        if not audio_path:
            return "", history
            
        history = history or []
        
        # Transcribe
        transcription = self.whisper.transcribe_audio_with_feedback(audio_path)
        
        # 系統訊息：[None, 訊息] 代表系統提示
        history.append([None, f"🎤 **Voice Input Detected**\n\n{transcription}"])
        
        result = self.whisper.transcribe_audio(audio_path)
        if result.get("text") and not result.get("error"):
            user_text = result["text"]
            
            # 加入使用者識別出的文字
            history.append([user_text, ""])
            
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
        Handle quick phrase using List of Lists format.
        """
        history = history or []
        
        phrase_template = Config.QUICK_PHRASES.get(phrase_key, "")
        if not phrase_template:
            return history
        
        phrase = phrase_template.replace("{language}", self.current_language)
        
        # 加入對話
        history.append([phrase, ""])
        
        response = ""
        for chunk in self.ollama.generate_response(phrase, self.current_language):
            response += chunk
            history[-1][1] = response
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
            
            # 🔴 重點修正 1: 移除 type="messages"，預設接受 List of Lists
            chatbot = gr.Chatbot(
                label="Conversation",
                height=400,
                show_label=True
            )
            
            with gr.Row():
                with gr.Column(scale=4):
                    text_input = gr.Textbox(
                        label="Type your message",
                        placeholder="e.g., How do I say 'thank you' in Spanish?",
                        lines=1
                    )
                with gr.Column(scale=1):
                    # 🔴 重點修正 2: 使用 sources (複數)，避開 source (單數) 的錯誤
                    audio_input = gr.Audio(
                        sources=["microphone"], 
                        type="filepath",
                        label="🎤 Or speak"
                    )
            
            gr.Markdown("### 🚀 Quick Phrases")
            with gr.Row():
                quick_buttons = []
                for phrase_key in Config.QUICK_PHRASES.keys():
                    btn = gr.Button(phrase_key) # size參數也先拿掉，保險起見
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
                # 使用 lambda 處理生成器
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
