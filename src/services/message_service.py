import logging
from telegram import Update, Bot
from src.config.config import Config
from src.models.player import Player

logger = logging.getLogger(__name__)

class MessageService:
    @staticmethod
    async def send_text(bot: Bot, recipient: Player, message: str, is_from_angel: bool = True) -> bool:
        """Send a text message to a recipient"""
        if not recipient.is_registered:
            return False
            
        icon = Config.ANGEL_ICON if is_from_angel else Config.MORTAL_ICON
        try:
            await bot.send_message(
                chat_id=recipient.chat_id,
                text=f"{icon}: {message}"
            )
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    @staticmethod
    async def send_media(update: Update, bot: Bot, recipient: Player) -> bool:
        """Send a media message to a recipient"""
        if not recipient.is_registered:
            return False
            
        message = update.message
        try:
            if message.photo:
                await bot.send_photo(
                    chat_id=recipient.chat_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption
                )
            elif message.video:
                await bot.send_video(
                    chat_id=recipient.chat_id,
                    video=message.video.file_id,
                    caption=message.caption
                )
            elif message.voice:
                await bot.send_voice(
                    chat_id=recipient.chat_id,
                    voice=message.voice.file_id
                )
            elif message.video_note:
                await bot.send_video_note(
                    chat_id=recipient.chat_id,
                    video_note=message.video_note.file_id
                )
            elif message.sticker:
                await bot.send_sticker(
                    chat_id=recipient.chat_id,
                    sticker=message.sticker.file_id
                )
            elif message.animation:
                await bot.send_animation(
                    chat_id=recipient.chat_id,
                    animation=message.animation.file_id
                )
            elif message.audio:
                await bot.send_audio(
                    chat_id=recipient.chat_id,
                    audio=message.audio.file_id
                )
            elif message.document:
                await bot.send_document(
                    chat_id=recipient.chat_id,
                    document=message.document.file_id
                )
            return True
        except Exception as e:
            logger.error(f"Error sending media: {e}")
            return False 