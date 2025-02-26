import logging
import datetime
from telegram.ext import Application, CommandHandler as TelegramCommandHandler
from telegram.ext import MessageHandler as TelegramMessageHandler
from telegram.ext import CallbackQueryHandler, ConversationHandler, filters

from src.config.config import Config
from src.models.player import PlayerManager
from src.utils.database import DatabaseHandler
from src.handlers.command_handler import CommandHandler

# Set up logging
Config.setup_directories()
logging.basicConfig(
    filename=f'{Config.LOG_DIR}/{datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")}.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    # Initialize components
    player_manager = PlayerManager()
    db_handler = DatabaseHandler(player_manager)
    command_handler = CommandHandler(player_manager, db_handler)
    
    # Load data
    try:
        db_handler.load_players()
        db_handler.load_chat_ids()
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return
    
    # Initialize bot
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(TelegramCommandHandler("start", command_handler.start))
    
    # Add conversation handler for sending messages
    conv_handler = ConversationHandler(
        entry_points=[TelegramCommandHandler("send", command_handler.send_command)],
        states={
            Config.CHOOSING: [
                CallbackQueryHandler(command_handler.start_angel, pattern="angel"),
                CallbackQueryHandler(command_handler.start_mortal, pattern="mortal")
            ],
            Config.ANGEL: [
                TelegramMessageHandler(filters.ALL & ~filters.COMMAND, command_handler.send_angel)
            ],
            Config.MORTAL: [
                TelegramMessageHandler(filters.ALL & ~filters.COMMAND, command_handler.send_mortal)
            ]
        },
        fallbacks=[TelegramCommandHandler("cancel", command_handler.cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main() 