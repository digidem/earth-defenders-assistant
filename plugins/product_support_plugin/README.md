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

- Python 3.10.1 or higher
- uv package manager (recommended)
- Dependencies listed in pyproject.toml

## Installation

1. Clone the repository:

## Usage

The plugin can be used in three ways:

- As a CLI tool for direct queries
- Through the Telegram bot interface
- By importing and calling from your Python code

To install dependencies with uv (recommended):

### Docker

To run the Awana Telegram Bot using Docker, you can use the following command:

```bash
docker run -v ./bot:/app/mapeo_docs -e TELEGRAM_BOT_TOKEN=xxx:xxx-xxx -e OPENAI_API_KEY=sk-proj-xxx communityfirst/awana_telegram_bot
```
