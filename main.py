import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import config
from handlers import (
    start, services_command, my_account, my_balance, 
    my_orders, help_command, button_callback, handle_text
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot"""
    
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
        return
    
    # Create the Application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("services", services_command))
    application.add_handler(CommandHandler("account", my_account))
    application.add_handler(CommandHandler("balance", my_balance))
    application.add_handler(CommandHandler("orders", my_orders))
    
    # Add message handler for keyboard buttons
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Add callback handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the Bot
    logger.info("Bot started successfully!")
    print("🤖 البوت بدأ العمل بنجاح!")
    print("اضغط Ctrl+C لإيقاف البوت")
    
    application.run_polling(allowed_updates=None)

if __name__ == '__main__':
    main()
