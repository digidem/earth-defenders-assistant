# Earth Defenders Assistant - AI API

A robust FastAPI-based AI service for the Earth Defenders Assistant project, featuring text-to-speech, audio transcription, document processing, and intelligent conversation management.

## 🚀 Features

- **Text-to-Speech (TTS)**: Google Cloud TTS integration with multiple voice options
- **Audio Transcription**: Speech-to-text using Groq's Whisper API
- **Document Processing**: PDF and CSV document upload and semantic search
- **Conversation Memory**: Vector-based conversation history with semantic search
- **Global Knowledge Base**: Shared knowledge repository for all users
- **Multi-Platform Support**: WhatsApp, Telegram, and web interfaces
- **Agent System**: Specialized AI agents for different tasks

## 🏗️ Architecture Improvements

### 1. **Structured Logging**
- **Enhanced Logger Configuration**: Multi-level logging with rotation and compression
- **Request Tracking**: Request ID middleware for end-to-end tracing
- **Structured Logs**: JSON-formatted logs with context information
- **Error Logging**: Separate error log files with detailed stack traces

```python
# Example structured logging
logger.info(
    "TTS audio generated successfully",
    extra={
        "text_length": len(text),
        "audio_path": audio_path,
        "audio_encoding": encoding,
    }
)
```

### 2. **Constants Over Magic Numbers**
- **Centralized Constants**: All magic numbers and strings moved to `core/constants.py`
- **Meaningful Names**: Descriptive constant names that explain their purpose
- **Configuration-Driven**: Constants can be overridden via configuration

```python
# Before
if file.size > 50 * 1024 * 1024:  # Magic number
    raise HTTPException(status_code=400, detail="File too large")

# After
if file.size > MAX_FILE_SIZE_BYTES:  # Named constant
    raise FileTooLargeError(MAX_FILE_SIZE_MB)
```

### 3. **Custom Exception Hierarchy**
- **Specific Exception Types**: Different exception classes for different error scenarios
- **Structured Error Responses**: Consistent error response format
- **Error Context**: Detailed error information for debugging

```python
# Custom exceptions with context
class TTSGenerationError(AIAPIException):
    def __init__(self, message: str, text_length: Optional[int] = None):
        super().__init__(
            message=message,
            error_code="TTS_GENERATION_ERROR",
            details={"text_length": text_length},
            status_code=500
        )
```

### 4. **Input Validation**
- **Comprehensive Validation**: File type, size, and content validation
- **Security Checks**: Path traversal and filename sanitization
- **Parameter Validation**: TTS parameters, language codes, etc.

```python
# Validation utilities
validate_audio_file(file)
validate_tts_parameters(text, pitch, speaking_rate)
validate_session_id(session_id)
```

### 5. **Error Handling**
- **Centralized Error Handler**: Consistent error response format
- **Exception Middleware**: Global exception handling with proper logging
- **Graceful Degradation**: Service continues operating even when components fail

```python
# Global exception handler
@fast_app.exception_handler(AIAPIException)
async def aiapi_exception_handler(request: Request, exc: AIAPIException):
    return await handle_aiapi_exception(request, exc)
```

## 📁 Project Structure

```
apps/ai_api/
├── eda_ai_api/
│   ├── api/
│   │   └── routes/           # API route handlers
│   ├── agents/               # AI agent implementations
│   ├── core/
│   │   ├── constants.py      # Application constants
│   │   ├── config.py         # Core configuration
│   │   ├── event_handlers.py # Startup/shutdown handlers
│   │   ├── messages.py       # Error messages
│   │   └── security.py       # Security utilities
│   ├── models/               # Pydantic models
│   └── utils/
│       ├── logger.py         # Logging configuration
│       ├── exceptions.py     # Custom exceptions
│       ├── validation.py     # Input validation
│       ├── error_handler.py  # Error handling utilities
│       ├── tts_service.py    # TTS service
│       ├── audio_utils.py    # Audio processing
│       ├── vector_memory.py  # Vector database operations
│       └── memory.py         # Conversation memory
├── main.py                   # Application entry point
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
AI_API_DEBUG=true
AI_API_CONVERSATION_HISTORY_LIMIT=5
AI_API_RELEVANT_HISTORY_LIMIT=3

# API Keys
GROQ_API_KEY=your_groq_key
GOOGLE_AI_STUDIO_API_KEY=your_google_key
GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH=path/to/service-account.json
```

### YAML Configuration
```yaml
services:
  ai_api:
    debug: true
    conversation_history_limit: 5
    relevant_history_limit: 3

api_keys:
  groq: "your_groq_key"
  google_ai_studio: "your_google_key"
  google_cloud:
    service_account_path: "credentials/google/service-account.json"
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Google Cloud credentials (for TTS)
- Groq API key (for transcription)
- ChromaDB (for vector storage)
- PocketBase (for conversation storage)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys

# Run the application
python -m eda_ai_api.main
```

### Development
```bash
# Run with auto-reload
uvicorn eda_ai_api.main:app --reload --port 8083

# Run tests
pytest tests/

# Format code
black eda_ai_api/
isort eda_ai_api/

# Lint code
flake8 eda_ai_api/
```

## 📊 API Endpoints

### Text-to-Speech
- `POST /api/tts/generate` - Generate speech from text
- `GET /api/tts/download/{filename}` - Download generated audio
- `POST /api/tts/generate-and-download` - Generate and download immediately
- `GET /api/tts/voices` - Get available voices
- `GET /api/tts/formats` - Get supported audio formats

### Audio Transcription
- `POST /api/transcription/transcribe` - Transcribe audio to text

### Document Processing
- `POST /api/documents/upload` - Upload and process documents
- `GET /api/documents/search` - Search document content
- `DELETE /api/documents/cleanup` - Clean up expired documents

### Global Knowledge
- `POST /api/global_knowledge/upload` - Upload to global knowledge base
- `GET /api/global_knowledge/search` - Search global knowledge
- `GET /api/global_knowledge/list` - List all documents
- `DELETE /api/global_knowledge/delete/{source}` - Delete document

### Message Handling
- `POST /api/message_handler/handle` - Process user messages with AI

## 🔒 Security Features

### Input Validation
- File type and size validation
- Path traversal prevention
- Filename sanitization
- Parameter validation

### Error Handling
- No sensitive information in error responses
- Structured error logging
- Graceful degradation

### File Security
- Temporary file handling
- Secure file path validation
- Automatic cleanup of temporary files

## 📈 Performance Optimizations

### Async Operations
- All I/O operations are async
- Non-blocking file processing
- Concurrent request handling

### Caching
- TTS service lazy initialization
- Vector database connection pooling
- Embedding model caching

### Resource Management
- Automatic cleanup of temporary files
- TTL-based document expiration
- Memory-efficient file processing

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
pytest tests/unit/

# Run with coverage
pytest --cov=eda_ai_api tests/
```

### Integration Tests
```bash
# Run integration tests
pytest tests/integration/

# Test with real services
pytest tests/integration/ --use-real-services
```

### Load Testing
```bash
# Run load tests
locust -f tests/load/locustfile.py
```

## 📝 Logging

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General application flow
- **WARNING**: Potential issues
- **ERROR**: Error conditions
- **CRITICAL**: Critical failures

### Log Format
```
2024-01-15 10:30:45.123 | INFO     | eda_ai_api.api.routes.tts_handler:generate_speech:45 | TTS audio generated successfully
```

### Log Files
- `api.log` - General application logs
- `api_errors.log` - Error-only logs
- Rotated automatically (100MB, 30 days retention)

## 🔧 Monitoring

### Health Checks
- `GET /api/health` - Application health status
- Database connectivity checks
- External service availability

### Metrics
- Request/response times
- Error rates
- File processing statistics
- Memory usage

### Alerting
- Error rate thresholds
- Response time alerts
- Service availability monitoring

## 🤝 Contributing

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Add unit tests for new features

### Pull Request Process
1. Create feature branch
2. Write tests
3. Update documentation
4. Submit pull request
5. Code review
6. Merge to main

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: support@earthdefenders.ai
- Documentation: `/docs` endpoint when running in debug mode
- Issues: GitHub Issues page

---

**Built with ❤️ for Earth Defenders Assistant**