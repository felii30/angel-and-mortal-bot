import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from src.config.config import Config
from src.services.player_service import PlayerService
from src.services.message_service import MessageService
from src.services.rate_limit_service import RateLimitService
from src.services.profile_service import ProfileService

logger = logging.getLogger(__name__)

# States for profile setup flow
SETTING_NICKNAME, SETTING_BIO, SETTING_INTERESTS = range(3, 6)

class CommandHandler:
    def __init__(self, player_service: PlayerService):
        self.player_service = player_service
        self.message_service = MessageService()
        self.rate_limit_service = RateLimitService()
        self.profile_service = ProfileService()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command"""
        username = update.message.chat.username.lower()
        
        if not self.player_service.is_registered(username):
            await update.message.reply_text("Sorry, you are not registered for this private event.")
            return
        
        player = self.player_service.register_player(username, update.message.chat.id)
        await update.message.reply_text(
            f"Welcome, {player.username}! 🎭\n\n"
            f"Available commands:\n"
            f"/send - Send a message to your angel or mortal\n"
            f"/setup - Set up your profile (nickname, bio, interests)\n"
            f"/profile - View your profile"
        )
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /profile command"""
        username = update.message.chat.username.lower()
        if not self.player_service.is_registered(username):
            await update.message.reply_text("Sorry, you are not registered for this private event.")
            return
            
        relationships = self.player_service.get_player_relationships(username)
        if not relationships:
            await update.message.reply_text("Error: Could not find your relationships.")
            return
            
        angel, mortal = relationships
        profile_summary = self.profile_service.get_full_profile_view(
            username,
            angel.username,
            mortal.username
        )
        await update.message.reply_text(profile_summary)
    
    async def setup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the profile setup process"""
        username = update.message.chat.username.lower()
        if not self.player_service.is_registered(username):
            await update.message.reply_text("Sorry, you are not registered for this private event.")
            return ConversationHandler.END
        
        await update.message.reply_text(
            "Let's set up your profile! 🎨\n\n"
            "First, please enter your preferred nickname:"
        )
        return SETTING_NICKNAME

    async def handle_nickname(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle nickname input and ask for bio"""
        username = update.message.chat.username.lower()
        nickname = update.message.text.strip()
        
        if len(nickname) > 32:
            await update.message.reply_text(
                "Nickname too long! Please keep it under 32 characters.\n"
                "Enter your nickname:"
            )
            return SETTING_NICKNAME
        
        self.profile_service.set_nickname(username, nickname)
        await update.message.reply_text(
            f"Great! Your nickname is set to: {nickname}\n\n"
            "Now, tell me a bit about yourself (your bio):"
        )
        return SETTING_BIO

    async def handle_bio(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle bio input and ask for interests"""
        username = update.message.chat.username.lower()
        bio = update.message.text.strip()
        
        if len(bio) > 300:
            await update.message.reply_text(
                "Bio too long! Please keep it under 300 characters.\n"
                "Enter your bio:"
            )
            return SETTING_BIO
        
        self.profile_service.set_bio(username, bio)
        await update.message.reply_text(
            "Perfect! Your bio is saved.\n\n"
            "Finally, what are your interests? (Enter multiple interests separated by commas)"
        )
        return SETTING_INTERESTS

    async def handle_interests(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle interests input and complete setup"""
        username = update.message.chat.username.lower()
        interests_text = update.message.text.strip()
        
        # Split interests by commas and clean them up
        interests = [
            interest.strip()
            for interest in interests_text.split(',')
            if interest.strip()
        ]
        
        # Add each interest
        for interest in interests:
            self.profile_service.add_interest(username, interest)
        
        # Show the complete profile
        profile_summary = self.profile_service.get_profile_summary(username)
        await update.message.reply_text(
            "🎉 Your profile is complete!\n\n" + profile_summary
        )
        return ConversationHandler.END
    
    async def send_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the /send command"""
        username = update.message.chat.username.lower()
        
        if not self.player_service.is_registered(username):
            await update.message.reply_text("Sorry, you are not registered for this private event.")
            return ConversationHandler.END
        
        if not self.rate_limit_service.can_send_message(username):
            remaining_time = self.rate_limit_service.get_remaining_time(username)
            await update.message.reply_text(
                f"You're sending messages too quickly! Please wait {int(remaining_time)} seconds."
            )
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
        relationships = self.player_service.get_player_relationships(username)
        
        if not relationships:
            await update.callback_query.message.reply_text("Error: Could not find your relationships.")
            return ConversationHandler.END
            
        angel, _ = relationships
        if not angel.is_registered:
            await update.callback_query.message.reply_text("Your angel has not started the bot yet.")
            return ConversationHandler.END
        
        await update.callback_query.message.reply_text("Please type your message to your Angel.")
        return Config.ANGEL
    
    async def start_mortal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start conversation with mortal"""
        username = update.callback_query.message.chat.username.lower()
        relationships = self.player_service.get_player_relationships(username)
        
        if not relationships:
            await update.callback_query.message.reply_text("Error: Could not find your relationships.")
            return ConversationHandler.END
            
        _, mortal = relationships
        if not mortal.is_registered:
            await update.callback_query.message.reply_text("Your mortal has not started the bot yet.")
            return ConversationHandler.END
        
        await update.callback_query.message.reply_text("Please type your message to your Mortal.")
        return Config.MORTAL
    
    async def send_angel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Send message to angel"""
        username = update.message.chat.username.lower()
        relationships = self.player_service.get_player_relationships(username)
        
        if not relationships:
            await update.message.reply_text("Error: Could not find your relationships.")
            return ConversationHandler.END
            
        angel, _ = relationships
        success = False
        is_media = not bool(update.message.text)
        
        if update.message.text:
            success = await self.message_service.send_text(
                context.bot,
                angel,
                update.message.text,
                is_from_angel=False
            )
        else:
            success = await self.message_service.send_media(
                update,
                context.bot,
                angel
            )
        
        if success:
            await update.message.reply_text("Your message has been sent to your Angel.")
            logger.info(f"{username} sent a message to their angel ({angel.username}).")
        else:
            await update.message.reply_text("Failed to send message to your Angel.")
        
        return ConversationHandler.END
    
    async def send_mortal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Send message to mortal"""
        username = update.message.chat.username.lower()
        relationships = self.player_service.get_player_relationships(username)
        
        if not relationships:
            await update.message.reply_text("Error: Could not find your relationships.")
            return ConversationHandler.END
            
        _, mortal = relationships
        success = False
        is_media = not bool(update.message.text)
        
        if update.message.text:
            success = await self.message_service.send_text(
                context.bot,
                mortal,
                update.message.text,
                is_from_angel=True
            )
        else:
            success = await self.message_service.send_media(
                update,
                context.bot,
                mortal
            )
        
        if success:
            await update.message.reply_text("Your message has been sent to your Mortal.")
            logger.info(f"{username} sent a message to their mortal ({mortal.username}).")
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