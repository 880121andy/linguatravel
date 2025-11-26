# LinguaTravel - Architecture Documentation

## Overview

LinguaTravel is a modular language learning assistant designed for travelers. The application follows a clean separation of concerns with distinct service layers for AI, speech recognition, and user interface.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Gradio Web UI                        │
│                     (src/ui.py)                         │
└─────────────┬───────────────────────┬───────────────────┘
              │                       │
              ▼                       ▼
    ┌─────────────────┐     ┌──────────────────┐
    │ Ollama Service  │     │ Whisper Service  │
    │ (ollama_service)│     │(whisper_service) │
    └────────┬────────┘     └────────┬─────────┘
             │                       │
             ▼                       ▼
    ┌─────────────────┐     ┌──────────────────┐
    │ Ollama Server   │     │  Whisper Model   │
    │   (External)    │     │    (Local)       │
    └─────────────────┘     └──────────────────┘
```

## Component Breakdown

### 1. Configuration Layer (`src/config.py`)

**Purpose**: Centralized configuration management

**Key Features**:
- Environment variable support
- Model configuration (Ollama, Whisper)
- Server settings
- Language and scenario definitions
- Device auto-detection for Whisper

**Design Decision**: Using a class-based config allows for easy testing and validation while supporting both hardcoded defaults and environment overrides.

### 2. Ollama Service (`src/ollama_service.py`)

**Purpose**: Manages all interactions with the Ollama LLM

**Responsibilities**:
- Health checking and connection management
- Model availability verification
- Model pulling/downloading
- Streaming response generation
- Conversation history management

**Key Methods**:
- `check_health()`: Verifies Ollama server connectivity
- `check_model_exists()`: Validates model availability
- `pull_model()`: Downloads models with progress updates
- `generate_response()`: Generates AI responses with streaming support
- `clear_history()`: Resets conversation context

**Design Decision**: Streaming responses provide better UX by showing real-time generation rather than waiting for complete responses.

### 3. Whisper Service (`src/whisper_service.py`)

**Purpose**: Handles speech-to-text conversion

**Responsibilities**:
- Whisper model loading and management
- Audio file transcription
- Language detection
- Error handling for corrupted/empty audio

**Key Methods**:
- `load_model()`: Initializes Whisper with device detection
- `transcribe_audio()`: Converts audio to text
- `transcribe_audio_with_feedback()`: User-friendly transcription with messages
- `get_status()`: Reports service status

**Design Decision**: Lazy loading of the model (on first use) reduces startup time. Device auto-detection ensures optimal performance across different hardware.

### 4. Gradio UI (`src/ui.py`)

**Purpose**: Provides interactive web interface

**Features**:
- Chat interface for conversations
- Audio recording for pronunciation practice
- Quick phrase buttons for common scenarios
- Language selector
- Status indicators
- Model setup interface

**Event Handlers**:
- `handle_text_message()`: Processes typed input
- `handle_audio_message()`: Processes voice input
- `handle_quick_phrase()`: Processes quick phrase buttons
- `update_language()`: Changes target language
- `clear_conversation()`: Resets chat
- `setup_model()`: Downloads Ollama model

**Design Decision**: Gradio was chosen for rapid prototyping and built-in audio support. The interface uses generator functions for streaming to provide responsive feedback.

### 5. Main Application (`app.py`)

**Purpose**: Application orchestration and startup

**Flow**:
1. Display banner
2. Validate configuration
3. Initialize Ollama service
4. Load Whisper model
5. Create UI
6. Launch Gradio server

**Error Handling**: Graceful degradation - the app can start even if Ollama is not running, with clear user guidance.

## Data Flow

### Text Conversation Flow
```
User Input → UI → Ollama Service → Ollama API → Response Stream → UI → User
```

### Voice Conversation Flow
```
User Audio → UI → Whisper Service → Transcription → UI Display
                                          ↓
                              Ollama Service → Response → UI → User
```

## Key Design Decisions

### 1. Modular Service Architecture
- **Rationale**: Separation of concerns makes testing easier and allows swapping implementations
- **Benefit**: Can easily replace Ollama with another LLM or Whisper with another STT service

### 2. Streaming Responses
- **Rationale**: Better user experience with real-time feedback
- **Benefit**: Users see responses as they're generated rather than waiting

### 3. Environment-Based Configuration
- **Rationale**: Flexibility for different deployment scenarios
- **Benefit**: Easy to customize without code changes

### 4. Graceful Error Handling
- **Rationale**: Provide clear, actionable error messages
- **Benefit**: Users can self-diagnose and fix common issues

### 5. Travel-Focused Prompting
- **Rationale**: Generic language learning is too broad
- **Benefit**: More relevant and practical responses for travelers

## Dependencies

### Core Dependencies
- **Gradio (>=4.0.0)**: Web UI framework
- **OpenAI Whisper (>=20231117)**: Speech recognition
- **Requests (>=2.31.0)**: HTTP client for Ollama API
- **PyTorch (>=2.0.0)**: Deep learning framework for Whisper

### External Services
- **Ollama**: Must be running locally on port 11434
- **FFmpeg**: Required for audio processing

## Performance Considerations

### Memory Usage
- Whisper `base` model: ~140MB
- Ollama `gemma2:2b`: ~1.5GB
- **Total**: ~2GB minimum recommended

### Startup Time
- Initial: 10-30 seconds (Whisper model loading)
- Subsequent: 2-5 seconds

### Response Time
- Text input: 1-3 seconds for first token
- Audio transcription: 1-2 seconds per 10 seconds of audio
- Streaming: Real-time display as generated

## Security Considerations

- Application runs locally only by default
- No data sent to external servers (except Ollama API locally)
- Audio recordings are temporary and not persisted
- Environment variables for sensitive configuration

## Future Enhancement Opportunities

1. **Conversation Export**: Save learning sessions
2. **Progress Tracking**: Track phrases learned and practice time
3. **Pronunciation Scoring**: Evaluate pronunciation accuracy
4. **Offline Mode**: Pre-download conversations for offline use
5. **Multi-User Support**: User profiles and personalized learning paths
