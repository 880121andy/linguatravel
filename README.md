# 🌍 LinguaTravel - Your Travel Language Assistant

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/Gradio-4.0%2B-orange.svg)](https://gradio.app/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A voice-enabled language learning assistant designed specifically for travelers. Practice common travel phrases, get instant translations, and improve your pronunciation using AI-powered conversation and speech recognition.

## ✨ Features

- 🎙️ **Voice Input**: Practice pronunciation with Whisper speech recognition
- 💬 **Interactive Conversations**: Natural language learning with Ollama AI
- 🚀 **Quick Phrases**: One-click access to common travel scenarios
- 🌐 **Multi-Language Support**: Learn Spanish, French, German, Italian, Japanese, Chinese, and more
- 📱 **Web Interface**: Easy-to-use Gradio interface accessible from any browser
- 🎯 **Travel-Focused**: Scenarios tailored for real travel situations

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify: `python --version`

2. **Ollama**
   - Download from [ollama.ai](https://ollama.ai/)
   - Verify: `ollama --version`

3. **FFmpeg** (for audio processing)
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or install via chocolatey: `choco install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)
   - Verify: `ffmpeg -version`

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/880121andy/linguatravel
cd linguatravel
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> ⏱️ **Note**: The first installation may take 5-10 minutes as it downloads the Whisper model and PyTorch dependencies.

### 4. Setup Ollama

Start the Ollama server:

```bash
ollama serve
```

In a new terminal, pull the required model:

```bash
ollama pull gemma2:2b
```

## 🎮 Usage

### Starting the Application

1. **Activate your virtual environment** (if not already activated):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Ensure Ollama is running**:
   ```bash
   ollama serve
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser**: The app will automatically open at `http://localhost:7860`

### Using the Interface

1. **Select Your Target Language**: Choose which language you want to learn from the dropdown menu

2. **Start Learning**:
   - **Type**: Enter questions or phrases in the text box
   - **Speak**: Click the microphone icon to practice pronunciation
   - **Quick Phrases**: Click scenario buttons for instant conversations

3. **Example Interactions**:
   - "How do I say 'where is the bathroom' in Spanish?"
   - "Teach me how to order food in French"
   - "What are common greetings in Japanese?"

## 🛠️ Configuration

You can customize the application using environment variables. Create a `.env` file in the project root:

```env
# Ollama Settings
OLLAMA_MODEL=gemma2:2b
OLLAMA_HOST=http://localhost:11434
OLLAMA_TIMEOUT=120

# Whisper Settings
WHISPER_MODEL=base
WHISPER_DEVICE=auto  # auto, cuda, or cpu

# Gradio Settings
GRADIO_PORT=7860
GRADIO_SHARE=False
```

### Model Options

**Ollama Models** (smaller = faster, larger = more capable):
- `gemma2:2b` (recommended for most systems)
- `llama3.2:3b`
- `phi3:mini`

**Whisper Models** (smaller = faster, larger = more accurate):
- `tiny` - Fastest, least accurate
- `base` - Good balance (recommended)
- `small` - Better accuracy
- `medium` - High accuracy, slower

## 🐛 Troubleshooting

### "Cannot connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check if Ollama is accessible: `curl http://localhost:11434`
- Verify the model is installed: `ollama list`

### "Model not found"
- Pull the model: `ollama pull gemma2:2b`
- Or use the "Setup Model" button in the UI

### "Port already in use"
- Change the port in `.env`: `GRADIO_PORT=7861`
- Or kill the process using port 7860

### "CUDA out of memory" or slow performance
- Use CPU for Whisper: `WHISPER_DEVICE=cpu` in `.env`
- Use a smaller Whisper model: `WHISPER_MODEL=tiny`
- Use a smaller Ollama model: `ollama pull phi3:mini`

### Audio recording not working
- Check browser permissions for microphone access
- Verify FFmpeg is installed: `ffmpeg -version`
- Try refreshing the browser page

## 📁 Project Structure

```
linguatravel/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── ollama_service.py    # Ollama integration
│   ├── whisper_service.py   # Whisper STT integration
│   └── ui.py                # Gradio interface
├── app.py                   # Main application entry
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .gitignore              # Git ignore rules
└── LICENSE                 # MIT License
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Ideas for Contribution

- Add more language support
- Create additional travel scenarios
- Improve pronunciation feedback
- Add conversation history export
- Implement progress tracking

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) - For the local LLM infrastructure
- [OpenAI Whisper](https://github.com/openai/whisper) - For speech recognition
- [Gradio](https://gradio.app/) - For the beautiful UI framework

## 📞 Support

Having issues? Here's how to get help:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing [GitHub Issues](https://github.com/yourusername/linguatravel/issues)
3. Create a new issue with:
   - Your OS and Python version
   - Error messages (full traceback)
   - Steps to reproduce the problem

---

**Happy Traveling! 🌍✈️**

Made with ❤️ for language learners and travelers worldwide.
