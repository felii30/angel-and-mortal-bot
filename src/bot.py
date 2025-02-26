import logging
import datetime
from telegram.ext import Application, CommandHandler as TelegramCommandHandler
from telegram.ext import MessageHandler as TelegramMessageHandler
from telegram.ext import CallbackQueryHandler, ConversationHandler, filters

from src.config.config import Config
from src.models.player import PlayerManager
from src.utils.database import DatabaseHandler
from src.services.player_service import PlayerService
from src.handlers.command_handler import CommandHandler, SETTING_NICKNAME, SETTING_BIO, SETTING_INTERESTS

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
    player_service = PlayerService(player_manager, db_handler)
    command_handler = CommandHandler(player_service)
    
    # Initialize data
    if not player_service.initialize_data():
        logger.error("Failed to initialize data. Exiting...")
        return
    
    # Initialize bot
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add basic command handlers
    application.add_handler(TelegramCommandHandler("start", command_handler.start))
    application.add_handler(TelegramCommandHandler("profile", command_handler.profile_command))
    
    # Add conversation handler for sending messages
    send_handler = ConversationHandler(
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
    
    # Add conversation handler for profile setup
    setup_handler = ConversationHandler(
        entry_points=[TelegramCommandHandler("setup", command_handler.setup_command)],
        states={
            SETTING_NICKNAME: [
                TelegramMessageHandler(filters.TEXT & ~filters.COMMAND, command_handler.handle_nickname)
            ],
            SETTING_BIO: [
                TelegramMessageHandler(filters.TEXT & ~filters.COMMAND, command_handler.handle_bio)
            ],
            SETTING_INTERESTS: [
                TelegramMessageHandler(filters.TEXT & ~filters.COMMAND, command_handler.handle_interests)
            ]
        },
        fallbacks=[TelegramCommandHandler("cancel", command_handler.cancel)]
    )
    
    # Add all handlers
    application.add_handler(send_handler)
    application.add_handler(setup_handler)
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main() 