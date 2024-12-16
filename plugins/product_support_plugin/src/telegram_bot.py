import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.main import initialize_grag, query
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor
load_dotenv()

# Initialize the GraphRAG once
grag = initialize_grag()
# Create a thread pool executor for running sync code
executor = ThreadPoolExecutor()

async def start_command(update, context):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Welcome to Mapeo Documentation Assistant! Ask me any questions about Mapeo."
    )

async def help_command(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "I can answer questions about Mapeo's features, components, and functionality.\n"
        "Just ask your question and I'll try to help!"
    )

async def handle_message(update, context):
    """Handle incoming messages and respond with answers from GraphRAG."""
    try:
        question = update.message.text
        if not question:
            await update.message.reply_text("Please enter a valid question.")
            return
            
        if question.lower() in ['exit', 'quit']:
            await update.message.reply_text("Goodbye!")
            return
            
        try:
            # Add thumbs up reaction to user's message
            # await update.message.set_message_reaction(reaction=["👍"])
            
            # Run the synchronous query in a thread pool
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(executor, query, question, grag)
            
            # Reply with markdown formatting, quoting the original message
            await update.message.reply_text(
                response,
                parse_mode='Markdown',
                do_quote=True
            )
        except Exception as e:
            await update.message.reply_text(f"An error occurred while processing your question: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

def main():
    """Start the bot."""
    print("Starting Mapeo Documentation Assistant bot...")

    # Get bot token from environment variable
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN environment variable not found")
        raise ValueError("Please set the TELEGRAM_BOT_TOKEN environment variable")
    print("Successfully loaded bot token")

    # Create application and pass it your bot's token
    print("Building Telegram application...")
    application = Application.builder().token(token).build()
    print("Successfully built Telegram application")

    # Add command handlers
    print("Registering command handlers...")
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    print("Successfully registered command handlers")
    
    # Add message handler
    print("Registering message handler...")
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Successfully registered message handler")

    # Start the bot
    print("Starting bot polling...")
    application.run_polling()
    print("Bot stopped")

if __name__ == "__main__":
    main()
