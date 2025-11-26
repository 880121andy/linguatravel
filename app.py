"""
LinguaTravel - Language Learning Assistant for Travellers
Main application entry point.

This application combines:
- Ollama for intelligent language learning conversations
- Whisper for speech recognition and pronunciation practice
- Gradio for an interactive web interface

Author: LinguaTravel Team
License: MIT
"""

import sys
from src.config import Config
from src.ollama_service import OllamaService
from src.whisper_service import WhisperService
from src.ui import LinguaTravelUI


def print_banner():
    """Print application banner."""
    print("=" * 60)
    print("🌍 LinguaTravel - Your Travel Language Assistant")
    print("=" * 60)
    print()


def check_prerequisites() -> bool:
    """
    Check if all prerequisites are met.
    
    Returns:
        bool: True if all prerequisites are met
    """
    print("🔍 Checking prerequisites...")
    
    # Validate configuration
    is_valid, error_msg = Config.validate_config()
    if not is_valid:
        print(f"❌ Configuration error: {error_msg}")
        return False
    
    print(f"✅ Configuration validated")
    print(f"   - Ollama Model: {Config.OLLAMA_MODEL}")
    print(f"   - Whisper Model: {Config.WHISPER_MODEL}")
    print(f"   - Device: {Config.get_whisper_device()}")
    print()
    
    return True


def initialize_services() -> tuple[OllamaService, WhisperService]:
    """
    Initialize all required services.
    
    Returns:
        tuple: (ollama_service, whisper_service)
    """
    print("🚀 Initializing services...")
    
    # Initialize Ollama
    print("   📡 Connecting to Ollama...")
    ollama_service = OllamaService()
    
    if not ollama_service.check_health():
        print("   ⚠️  Ollama server not detected.")
        print("   💡 Please start Ollama with: ollama serve")
        print("   ℹ️  You can still launch the app, but you'll need to start Ollama before using it.")
        print()
    else:
        print(f"   ✅ Connected to Ollama at {Config.OLLAMA_HOST}")
        
        if not ollama_service.check_model_exists():
            print(f"   ⚠️  Model '{Config.OLLAMA_MODEL}' not found locally.")
            print(f"   💡 Click 'Setup Model' in the UI to download it, or run:")
            print(f"      ollama pull {Config.OLLAMA_MODEL}")
            print()
        else:
            print(f"   ✅ Model '{Config.OLLAMA_MODEL}' is ready")
    
    # Initialize Whisper
    print("   🎤 Loading Whisper model...")
    whisper_service = WhisperService()
    success, message = whisper_service.load_model()
    print(f"   {message}")
    
    print()
    return ollama_service, whisper_service


def main():
    """Main application function."""
    try:
        print_banner()
        
        # Check prerequisites
        if not check_prerequisites():
            print("\n❌ Prerequisites check failed. Please fix the errors above.")
            sys.exit(1)
        
        # Initialize services
        ollama_service, whisper_service = initialize_services()
        
        # Create UI
        print("🎨 Building user interface...")
        ui = LinguaTravelUI(ollama_service, whisper_service)
        interface = ui.create_interface()
        
        print("✅ Interface ready!")
        print()
        print("=" * 60)
        print("🌟 Starting LinguaTravel...")
        print(f"🌐 Opening browser at http://localhost:{Config.GRADIO_PORT}")
        print("=" * 60)
        print()
        print("💡 Press Ctrl+C to stop the server")
        print()
        
        # Launch Gradio
        interface.launch(
            server_port=Config.GRADIO_PORT,
            share=Config.GRADIO_SHARE,
            inbrowser=True
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down LinguaTravel. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Application error: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure Ollama is running: ollama serve")
        print("   2. Check if the port is available")
        print("   3. Verify all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
