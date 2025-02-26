import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from src.config.config import Config
from src.models.player import PlayerManager
from src.handlers.message_handler import MessageHandler
from src.utils.database import DatabaseHandler

logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self, player_manager: PlayerManager, db_handler: DatabaseHandler):
        self.player_manager = player_manager
        self.db_handler = db_handler
        self.message_handler = MessageHandler()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command"""
        username = update.message.chat.username.lower()
        player = self.player_manager.get_player(username)
        
        if not player:
            await update.message.reply_text("Sorry, you are not registered for this private event.")
            return
        
        player.chat_id = update.message.chat.id
        self.db_handler.save_chat_ids()
        
        await update.message.reply_text(
            f"Welcome, {player.username}! You can use /send to send a message to your angel or mortal."
        )
    
    async def send_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the /send command"""
        username = update.message.chat.username.lower()
        player = self.player_manager.get_player(username)
        
        if not player:
            await update.message.reply_text("Sorry, you are not registered for this private event.")
            return ConversationHandler.END
        
        send_menu = [
            [InlineKeyboardButton("Angel", callback_data='angel')],
            [InlineKeyboardButton("Mortal", callback_data='mortal')]
        ]
        reply_markup = InlineKeyboardMarkup(send_menu)
        await update.message.reply_text("Send a message to your:", reply_markup=reply_markup)
        
        return Config.CHOOSING
    
    async def start_angel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start conversation with angel"""
        username = update.callback_query.message.chat.username.lower()
        player = self.player_manager.get_player(username)
        
        if not player.angel.is_registered:
            await update.callback_query.message.reply_text("Your angel has not started the bot yet.")
            return ConversationHandler.END
        
        await update.callback_query.message.reply_text("Please type your message to your Angel.")
        return Config.ANGEL
    
    async def start_mortal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start conversation with mortal"""
        username = update.callback_query.message.chat.username.lower()
        player = self.player_manager.get_player(username)
        
        if not player.mortal.is_registered:
            await update.callback_query.message.reply_text("Your mortal has not started the bot yet.")
            return ConversationHandler.END
        
        await update.callback_query.message.reply_text("Please type your message to your Mortal.")
        return Config.MORTAL
    
    async def send_angel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Send message to angel"""
        username = update.message.chat.username.lower()
        player = self.player_manager.get_player(username)
        
        success = False
        if update.message.text:
            success = await self.message_handler.send_message(
                context.bot,
                player.angel,
                update.message.text,
                is_from_angel=False
            )
        else:
            success = await self.message_handler.send_media(
                update,
                context.bot,
                player.angel,
                is_from_angel=False
            )
        
        if success:
            await update.message.reply_text("Your message has been sent to your Angel.")
            logger.info(f"{username} sent a message to their angel ({player.angel.username}).")
        else:
            await update.message.reply_text("Failed to send message to your Angel.")
        
        return ConversationHandler.END
    
    async def send_mortal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Send message to mortal"""
        username = update.message.chat.username.lower()
        player = self.player_manager.get_player(username)
        
        success = False
        if update.message.text:
            success = await self.message_handler.send_message(
                context.bot,
                player.mortal,
                update.message.text,
                is_from_angel=True
            )
        else:
            success = await self.message_handler.send_media(
                update,
                context.bot,
                player.mortal,
                is_from_angel=True
            )
        
        if success:
            await update.message.reply_text("Your message has been sent to your Mortal.")
            logger.info(f"{username} sent a message to their mortal ({player.mortal.username}).")
        else:
            await update.message.reply_text("Failed to send message to your Mortal.")
        
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the conversation"""
        await update.message.reply_text(
            "Message sending cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END 