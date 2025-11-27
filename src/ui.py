"""
Gradio UI for LinguaTravel application.
TARGET: Gradio 6.0+ (Implicit Messages Mode)
"""

import gradio as gr
from typing import List, Tuple, Optional, Union, Any
from packaging import version
from .config import Config
from .ollama_service import OllamaService
from .whisper_service import WhisperService
from .utils.history import normalize_history

# Compatibility shim for Gradio 6+ vs older versions
GRADIO_V6 = version.parse(gr.__version__) >= version.parse("6.0.0")


def to_internal_history(history: Optional[Any]) -> List[dict]:
    """
    Convert incoming Gradio history payloads to internal dict-list format.
    
    Accepts various formats including:
    - Gradio 6.x format: list of [user_msg, bot_msg] pairs
    - Gradio 7.x format: list of dicts with role/content keys
    - Other formats: normalized first via normalize_history()
    
    Returns:
        List of dicts with "role" and "content" keys.
    """
    if not history:
        return []
    
    # Ensure history is a list/iterable with at least one item
    if not isinstance(history, (list, tuple)) or len(history) == 0:
        return []
    
    # Check if already in internal dict format (role/content dicts)
    if isinstance(history[0], dict) and "role" in history[0]:
        return list(history)
    
    # Normalize the history first to Gradio 6.x format (list of [user, bot] pairs)
    # This handles various input formats including v7 dicts, tuples, etc.
    normalized = normalize_history(history)
    
    # Convert normalized pairs to internal dict format
    internal = []
    for user_msg, assistant_msg in normalized:
        if user_msg:
            internal.append({"role": "user", "content": user_msg})
        if assistant_msg:
            internal.append({"role": "assistant", "content": assistant_msg})
    return internal


def to_gradio_history(history: List[dict]) -> Union[List[dict], List[Tuple[str, str]]]:
    """
    Convert internal dict-list history back to Gradio-compatible format.
    
    For Gradio 6+: return dict format as-is.
    For older Gradio: convert to list of tuples [(user_msg, assistant_msg), ...]
    """
    if not history:
        return []
    
    if GRADIO_V6:
        return history
    
    # Convert to legacy tuple format for older Gradio
    # Group messages into (user, assistant) pairs
    legacy = []
    i = 0
    while i < len(history):
        user_content = ""
        assistant_content = ""
        
        # Collect consecutive user messages
        while i < len(history) and history[i].get("role") == "user":
            if user_content:
                user_content += "\n"
            user_content += history[i].get("content", "")
            i += 1
        
        # Collect consecutive assistant messages
        while i < len(history) and history[i].get("role") == "assistant":
            if assistant_content:
                assistant_content += "\n"
            assistant_content += history[i].get("content", "")
            i += 1
        
        # Only add if we have at least one message
        if user_content or assistant_content:
            legacy.append((user_content, assistant_content))
        
        # Handle any unexpected role by skipping
        if i < len(history) and history[i].get("role") not in ("user", "assistant"):
            i += 1
    
    return legacy

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
        """
        [Corrected] Handle text message using Dictionary format.
        """
        # Convert incoming history to internal format
        history = to_internal_history(history)
        
        if not message.strip():
            return "", to_gradio_history(history)
        
        # 1. 加入使用者訊息 (Dictionary 格式)
        history.append({"role": "user", "content": message})
        
        # 2. 加入 AI 預備訊息
        history.append({"role": "assistant", "content": ""})
        
        response = ""
        for chunk in self.ollama.generate_response(message, self.current_language):
            response += chunk
            # 3. 更新最後一條訊息
            history[-1]["content"] = response
            yield "", to_gradio_history(history)
        
        return "", to_gradio_history(history)
    
    def handle_audio_message(
        self,
        audio_path: Optional[str],
        history: List[dict]
    ) -> Tuple[str, List[dict]]:
        """
        [Corrected] Handle audio message using Dictionary format.
        """
        # Convert incoming history to internal format
        history = to_internal_history(history)
        
        if not audio_path:
            return "", to_gradio_history(history)
        
        transcription = self.whisper.transcribe_audio_with_feedback(audio_path)
        
        # 系統回饋 (模擬成 assistant 訊息)
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
                yield "", to_gradio_history(history)
        
        return "", to_gradio_history(history)
    
    def handle_quick_phrase(
        self,
        phrase_key: str,
        history: List[dict]
    ) -> List[dict]:
        """
        [Corrected] Handle quick phrase using Dictionary format.
        """
        # Convert incoming history to internal format
        history = to_internal_history(history)
        
        phrase_template = Config.QUICK_PHRASES.get(phrase_key, "")
        if not phrase_template:
            return to_gradio_history(history)
        
        phrase = phrase_template.replace("{language}", self.current_language)
        
        history.append({"role": "user", "content": phrase})
        history.append({"role": "assistant", "content": ""})
        
        response = ""
        for chunk in self.ollama.generate_response(phrase, self.current_language):
            response += chunk
            history[-1]["content"] = response
            yield to_gradio_history(history)
        
        return to_gradio_history(history)
    
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
            
            # 🟢 關鍵修改：
            # 1. 不加 type="messages" (避免 6.0 報錯)
            # 2. 上面的函數全部使用 Dictionary 格式 (滿足 6.0 的資料要求)
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
                    # 使用 4.0+ / 6.0+ 的 sources 參數
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
