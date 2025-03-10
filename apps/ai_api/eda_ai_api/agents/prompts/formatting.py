"""
WhatsApp formatting guidelines for the AI assistant.
"""

WHATSAPP_FORMATTING = """WhatsApp Format Guidelines:
- Format your final answers for WhatsApp messaging
- Keep responses concise and mobile-friendly (ideally under 300 words)
- Use *asterisks* for bold text instead of markdown
- Use _underscores_ for italics
- Use bullet points (•) for lists, not dashes
- Break long messages into paragraphs with line breaks
- Include emojis where appropriate for a friendly tone
- Avoid complex tables or ASCII art
- For code snippets, use single backticks `like this`
"""

# You can add more platform-specific formatting guidelines
TELEGRAM_FORMATTING = """Telegram Format Guidelines:
- Format your final answers for Telegram messaging
- Use **double asterisks** for bold text
- Use __double underscores__ for italics
- Use `backticks` for inline code
- Use ```triple backticks``` for code blocks
- Use unordered lists with hyphens
- Include emojis where appropriate
"""


# Add a function to get formatting based on platform
def get_formatting_guidelines(platform: str) -> str:
    """
    Returns formatting guidelines based on platform.

    Args:
        platform: The platform name (e.g., "whatsapp", "telegram")

    Returns:
        str: The formatting guidelines for the specified platform
    """
    platform = platform.lower()

    if platform == "whatsapp":
        return WHATSAPP_FORMATTING
    elif platform == "telegram":
        return TELEGRAM_FORMATTING
    else:
        # Default to WhatsApp formatting
        return WHATSAPP_FORMATTING
