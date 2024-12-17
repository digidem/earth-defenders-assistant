# Whatsapp

A WhatsApp integration module for the Earth Defenders Assistant platform using Baileys library.

## Requirements

- [Bun](https://bun.sh) v1.1.24 or higher
- Node.js environment
- WhatsApp account with an active phone number

## Environment Setup

1. Create a `.env` file in the root directory by copying `.env.example`:
```bash
cp .env.example .env
```

2. Configure the environment variables in your `.env` file.

## Installation

To install dependencies:

1. Go into the repo's main folder `./earth-defenders-assistant` and use:
```bash
bun install
```

2. Then use:
```bash
bun dev:whatsapp
```

## First-time Setup

1. When you first run the application, a QR code will appear in your terminal
2. Scan this QR code with your WhatsApp mobile app
3. Wait for the authentication process to complete
4. The bot will be ready to receive and process messages once connected

## Usage

- Use the configured `CMD_PREFIX` (default: "!") to send commands to the bot
- The bot will respond with messages prefixed with the configured `BOT_PREFIX`
- Reactions can be enabled/disabled using the `ENABLE_REACTIONS` setting

## Project Structure

This project is part of the Earth Defenders Assistant platform and uses:
- `@whiskeysockets/baileys` for WhatsApp integration
- Trigger.dev for workflow automation

For more information about the Earth Defenders Assistant platform and its components, please refer to the main project documentation.