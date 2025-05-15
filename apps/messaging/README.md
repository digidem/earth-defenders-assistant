# Earth Defenders Assistant - Messaging API

![Badge](https://img.shields.io/badge/Built%20with-Elysia-purple)
![Badge](https://img.shields.io/badge/Documentation-Swagger-green)
![Badge](https://img.shields.io/badge/Runtime-Bun-black)

A robust messaging API service built with Elysia.js for handling cross-platform messaging in the Earth Defenders Assistant ecosystem. This API provides seamless integration for WhatsApp, Telegram, and Simulator platforms with AI-powered message processing capabilities.

## Features

- **Cross-Platform Support**: Handle messages from WhatsApp, Telegram, and Simulator
- **AI Integration**: Process messages through integrated AI services
- **Audio Message Support**: Handle and process audio messages
- **Conversation History**: Track and maintain conversation history using Supabase
- **Real-time Monitoring**: Monitor API calls and performance using Trigger.dev
- **Swagger Documentation**: Built-in API documentation
- **Health Monitoring**: Endpoint for service health checks

## Prerequisites

- Bun Runtime
- Supabase Account
- Required API Keys (configured in config.yaml)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
bun install
```

## Usage

### Development
```bash
bun run dev
```

### Production Build
```bash
bun run build
```

### Start Production Server
```bash
bun run start
```

## API Endpoints

### Send Message
```http
POST /api/messages/send
```

Request Body:
```json
{
  "message": "Hello world",
  "sessionId": "5515991306053",
  "audio": "base64-encoded-audio-string", // Optional
  "platform": "whatsapp" // Optional: "whatsapp" | "telegram" | "simulator"
}
```

### Health Check
```http
GET /api/messages/health
```

## Development

### Available Scripts

- `bun run dev` - Start development server with hot reload
- `bun run build` - Build for production
- `bun run start` - Start production server
- `bun run test` - Run tests
- `bun run lint` - Run linting
- `bun run format` - Format code
- `bun run typecheck` - Check types

### Project Structure

```
src/
├── index.ts      # Main application entry
├── routes.ts     # API route handlers
└── types.ts      # TypeScript type definitions
```

## Error Handling

The API implements comprehensive error handling with:
- Input validation using Zod
- Detailed error logging
- Standardized error responses
- Monitoring of failed API calls

## Documentation

Swagger documentation is automatically generated and available at:
```
http://localhost:3001/swagger
```
