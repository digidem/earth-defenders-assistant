# Product Support Plugin

A RAG (Retrieval Augmented Generation) plugin for analyzing product support based on given documentation to identify key features, user interactions, data collection methods, and how different components of the platform work together.

## Overview

This plugin processes documentation from Mapeo, an offline-first mapping and monitoring platform, to provide insights about:

- Key features and functionality
- User interaction patterns
- Data collection methodologies
- Component integrations
- System architecture

## Requirements

- Python 3.10.1 or higher (< 4.0.0)
- libomp-dev (`sudo apt install libomp-dev`)
- Dependencies:
  - fast-graphrag
  - python-dotenv
  - python-telegram-bot >= 21.7

## Usage

The plugin provides several ways to interact with the product support system:

- CLI tool: `uv run product-support-cli`
- Telegram bot: `uv run product-support-telegram`
- Python API: Import and use `src.main.initialize_grag()` or `src.main.query()`

Example Python usage:

### Docker

To run the Awana Telegram Bot using Docker, you can use the following command:

```bash
docker run -v ./bot:/app/mapeo_docs -e TELEGRAM_BOT_TOKEN=xxx:xxx-xxx -e OPENAI_API_KEY=sk-proj-xxx communityfirst/awana_telegram_bot
```
