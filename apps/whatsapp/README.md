# WhatsApp Integration

A comprehensive WhatsApp integration module for the Earth Defenders Assistant platform using the Baileys library. This module provides AI-powered conversation capabilities, document processing, audio transcription, text-to-speech, and group message management.

## Features

### 🤖 AI-Powered Conversations
- **Intelligent Message Handling**: Processes text messages through the AI API for contextual responses
- **Multi-Modal Support**: Handles text, images, audio, and documents in a single conversation
- **Conversation Memory**: Maintains context across conversation sessions
- **Platform Integration**: Seamlessly integrates with the Earth Defenders Assistant AI backend

### 📄 Document Processing
- **PDF & CSV Support**: Upload and process documents for AI analysis
- **Automatic Storage**: Documents are stored with configurable TTL (Time To Live)
- **Group & Private**: Different TTL settings for group vs private conversations
- **Metadata Tracking**: Tracks sender information and upload timestamps

### 🎵 Audio Features
- **Voice Message Transcription**: Automatically transcribes audio messages to text
- **Text-to-Speech**: Generates voice responses for longer messages
- **Multi-Format Support**: Handles various audio formats (OGG Opus, MP3, WAV)
- **Language Detection**: Supports multiple languages for transcription and TTS

### 👥 Group Management
- **Smart Group Handling**: Only responds when mentioned or when quoting bot messages
- **Message Storage**: Automatically stores all group messages for analysis
- **Admin Controls**: Admin-only commands for group management
- **User Access Control**: Configurable allow/block lists for users

### 🔧 Command System
- **Built-in Commands**: `!help`, `!ping` with extensible command framework
- **Admin Commands**: Restricted commands for group administrators
- **Help System**: Comprehensive help documentation for all commands
- **Error Handling**: User-friendly error messages and validation

## Requirements

- [Bun](https://bun.sh) v1.1.24 or higher
- Node.js environment
- WhatsApp account with an active phone number
- Earth Defenders Assistant AI API running
- Google Cloud TTS credentials (for text-to-speech features)

## Installation

1. Navigate to the project root directory:
```bash
cd earth-defenders-assistant
```

2. Install dependencies:
```bash
bun install
```

3. Start the WhatsApp client in development mode:
```bash
bun dev:whatsapp
```

## First-time Setup

1. **QR Code Authentication**: When you first run the application, a QR code will appear in your terminal
2. **WhatsApp Scan**: Scan this QR code with your WhatsApp mobile app
3. **Authentication**: Wait for the authentication process to complete
4. **Ready State**: The bot will be ready to receive and process messages once connected

## Configuration

### Core Settings
- **Command Prefix**: Configure the command prefix (default: `!`)
- **Bot Prefix**: Set the bot's response prefix for identification
- **Reactions**: Enable/disable message reactions for status feedback
- **TTS**: Enable/disable text-to-speech for voice responses

### Access Control
- **Allowed Users**: List of phone numbers allowed to interact with the bot
- **Blocked Users**: List of phone numbers blocked from bot interaction
- **Group Access**: Control which groups the bot can operate in

### API Integration
- **AI API Base URL**: Endpoint for the Earth Defenders Assistant AI API
- **API Timeout**: Request timeout settings for API calls
- **Reconnection**: Automatic reconnection settings for connection stability

### Audio Processing
- **Transcription Language**: Default language for audio transcription
- **TTS Settings**: Text-to-speech configuration and thresholds
- **Audio Formats**: Supported audio formats and MIME types

## Usage

### Basic Commands
- `!help` - Show available commands and usage
- `!help <command>` - Get detailed help for a specific command
- `!ping` - Test if the bot is responsive

### Message Types

#### Text Messages
- Send any text message to start a conversation
- The bot will process your message through the AI API
- Responses include contextual information and follow-up suggestions

#### Audio Messages
- Send voice messages for automatic transcription
- Transcribed text is processed through the AI system
- Longer responses may include generated voice replies

#### Documents
- Upload PDF or CSV files for processing
- Documents are analyzed and stored with configurable TTL
- Processing results are returned with relevant insights

#### Images
- Send images with or without captions
- Images are processed alongside text for comprehensive analysis
- Multi-modal responses provide enhanced context

### Group Interactions
- **Mention Required**: In groups, mention the bot (`@bot_name`) to get responses
- **Quote Responses**: Reply to the bot's messages for follow-up interactions
- **Admin Commands**: Group admins have access to additional management commands
- **Message Storage**: All group messages are automatically stored for analysis

### Private Conversations
- **Direct Access**: Private messages are processed immediately
- **Full Features**: Access to all bot features in private chats
- **User Control**: Subject to allow/block list restrictions

## Technical Architecture

### Message Processing Pipeline
1. **Message Reception**: Baileys library receives WhatsApp messages
2. **Validation**: Messages are validated against access controls
3. **Type Detection**: Message type is determined (text, audio, document, image)
4. **Processing**: Appropriate handler processes the message
5. **AI Integration**: Processed content is sent to AI API
6. **Response Generation**: AI response is formatted and sent back
7. **TTS Generation**: Voice responses are generated for longer messages

### Dependencies
- **@whiskeysockets/baileys**: WhatsApp Web API implementation
- **@eda/config**: Centralized configuration management
- **@eda/logger**: Structured logging system
- **common-tags**: Template literal utilities
- **pino**: High-performance logging

## Error Handling

### Connection Issues
- **Automatic Reconnection**: Handles connection drops with exponential backoff
- **QR Code Regeneration**: Automatically regenerates QR codes when needed
- **Credential Management**: Secure storage and management of authentication

### API Errors
- **Timeout Handling**: Configurable timeouts with user-friendly error messages
- **Retry Logic**: Automatic retries for transient failures
- **Fallback Responses**: Graceful degradation when services are unavailable

### User Experience
- **Status Reactions**: Visual feedback through message reactions
- **Progress Indicators**: "Working" status messages during processing
- **Error Messages**: Clear, actionable error messages for users

## Monitoring and Logging

### Logging Levels
- **Info**: Normal operation events and user interactions
- **Warning**: Non-critical issues and access control events
- **Error**: API failures, connection issues, and processing errors
- **Debug**: Detailed debugging information for development

### Metrics Tracked
- Message processing times
- API response times
- Error rates and types
- User interaction patterns
- File upload success rates

## Security Considerations

### Access Control
- **User Whitelisting**: Only allowed users can interact with the bot
- **Group Restrictions**: Configurable group access controls
- **Admin Commands**: Restricted administrative functions

### Data Privacy
- **Message Storage**: Configurable TTL for stored messages
- **File Handling**: Secure file upload and processing
- **Credential Security**: Secure storage of authentication credentials

### API Security
- **Request Validation**: Input validation for all API requests
- **Error Sanitization**: Safe error messages without sensitive information
- **Rate Limiting**: Built-in rate limiting for API calls

## Troubleshooting

### Common Issues

#### Connection Problems
- **QR Code Not Appearing**: Check network connectivity and restart the application
- **Authentication Failed**: Clear authentication files and restart
- **Frequent Disconnections**: Check network stability and firewall settings

#### Message Processing Issues
- **No Response**: Verify AI API is running and accessible
- **Audio Transcription Fails**: Check audio format support and API credentials
- **Document Upload Errors**: Verify file format and size limits

#### Performance Issues
- **Slow Responses**: Check API response times and network latency
- **Memory Usage**: Monitor for memory leaks in long-running sessions
- **Queue Backlog**: Check message processing queue for bottlenecks

### Debug Mode
Enable debug logging by modifying the logger configuration in `client.ts`:
```typescript
const logger = P({ level: "debug" });
```

## Contributing

When contributing to the WhatsApp integration:

1. **Follow Code Style**: Use TypeScript with strict type checking
2. **Add Tests**: Include tests for new features and bug fixes
3. **Update Documentation**: Keep this README and code comments current
4. **Error Handling**: Implement proper error handling for all new features
5. **Configuration**: Use the centralized config system for all settings

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the configuration settings
3. Check the main project documentation
4. Open an issue in the project repository

---

For more information about the Earth Defenders Assistant platform and its components, please refer to the main project documentation.