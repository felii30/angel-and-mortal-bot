import json
import os
import logging
import datetime
import csv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Ensure the logs directory exists
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Set up logging using timezone-aware UTC datetimes
logging.basicConfig(
    filename=f'logs/{datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")}.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Constants for conversation handler states
CHOOSING, ANGEL, MORTAL = range(3)

# File paths for saving player data
PLAYER_DATA_FILE = "players.csv"
CHAT_ID_JSON = "chat_ids.json"

# Placeholder for players data
players = {}

# Player class to manage each player's information
class Player:
    def __init__(self):
        self.username = None
        self.angel = None
        self.mortal = None
        self.chat_id = None

# Function to load player data from a CSV file and set up angel/mortal pairings
# Function to load player data from a CSV file and set up angel/mortal pairings
# Bot cannot receive
def loadPlayers(players: dict):
    with open(PLAYER_DATA_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        rows = list(csv_reader)  # Load CSV data into a list for two-pass processing

        # First pass: Load players into the dictionary
        for i, row in enumerate(rows):
            if i == 0:
                logger.info(f'Column names are {", ".join(row)}')
                continue
            playerName = row[0].strip().lower()
            players[playerName] = Player()  # Add player
            players[playerName].username = playerName

        # Second pass: Assign angels and mortals
        for i, row in enumerate(rows):
            if i == 0:
                continue
            playerName = row[0].strip().lower()
            angelName = row[1].strip().lower()
            mortalName = row[2].strip().lower()

            # Now we can safely assign angels and mortals
            players[playerName].angel = players.get(angelName)
            players[playerName].mortal = players.get(mortalName)

            logger.info(f'{playerName} has angel {angelName} and mortal {mortalName}.')

    logger.info(f'Processed {len(rows) - 1} players.')
    validatePairings(players)
    loadChatID(players)

# Function to validate that each angel and mortal pairing is correct
def validatePairings(players: dict):
    for player in players.values():
        if player.angel.mortal.username != player.username or player.mortal.angel.username != player.username:
            logger.error(f'Error with {player.username} pairings')
            exit(1)

    logger.info(f'Validation complete, no issues with pairings.')

# Function to load chat IDs from a JSON file
def loadChatID(players: dict):
    try:
        with open(CHAT_ID_JSON, 'r') as f:
            temp = json.load(f)

            for k, v in temp.items():
                if k in players:
                    players[k].chat_id = v
            logger.info(f"Chat IDs loaded: {temp}")
    except FileNotFoundError:
        logger.warning('Chat ID JSON file not found, creating new file.')

# Function to save chat IDs to a JSON file
def saveChatID(players: dict):
    temp = {k: v.chat_id for k, v in players.items()}
    
    with open(CHAT_ID_JSON, 'w') as f:
        json.dump(temp, f, indent=4)
    logger.info("Chat IDs saved successfully.")

# Command to start the bot and save the chat ID
async def start(update: Update, context):
    username = update.message.chat.username.lower()

    if username not in players:
        await update.message.reply_text("Sorry, you are not registered for this private event.")
        return

    # Update chat ID when the user starts the bot
    players[username].chat_id = update.message.chat.id
    saveChatID(players)

    await update.message.reply_text(f"Welcome, {players[username].username}! You can use /send to send a message to your angel or mortal.")

# Command to send a message to an angel or mortal
async def send_command(update: Update, context):
    username = update.message.chat.username.lower()
    
    if username not in players:
        await update.message.reply_text("Sorry, you are not registered for this private event.")
        return ConversationHandler.END

    send_menu = [[InlineKeyboardButton("Angel", callback_data='angel')],
                 [InlineKeyboardButton("Mortal", callback_data='mortal')]]
    reply_markup = InlineKeyboardMarkup(send_menu)
    await update.message.reply_text("Send a message to your:", reply_markup=reply_markup)

    return CHOOSING

# Helper function to send non-text messages
async def send_non_text_message(update: Update, bot, chat_id):
    message = update.message

    if message.photo:
        await bot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id, caption=message.caption)
    elif message.video:
        await bot.send_video(chat_id=chat_id, video=message.video.file_id, caption=message.caption)
    elif message.voice:
        await bot.send_voice(chat_id=chat_id, voice=message.voice.file_id)
    elif message.video_note:
        await bot.send_video_note(chat_id=chat_id, video_note=message.video_note.file_id)
    elif message.sticker:
        await bot.send_sticker(chat_id=chat_id, sticker=message.sticker.file_id)
    elif message.animation:
        await bot.send_animation(chat_id=chat_id, animation=message.animation.file_id)
    elif message.audio:
        await bot.send_audio(chat_id=chat_id, audio=message.audio.file_id)
    elif message.document:
        await bot.send_document(chat_id=chat_id, document=message.document.file_id)

# Start conversation with angel
async def start_angel(update: Update, context):
    username = update.callback_query.message.chat.username.lower()
    angel_username = players[username].angel.username

    if players[angel_username].chat_id is None:
        await update.callback_query.message.reply_text(f"Your angel has not started the bot yet.")
        return ConversationHandler.END

    await update.callback_query.message.reply_text("Please type your message to your Angel.")
    return ANGEL

# Start conversation with mortal
async def start_mortal(update: Update, context):
    username = update.callback_query.message.chat.username.lower()
    mortal_username = players[username].mortal.username

    if players[mortal_username].chat_id is None:
        await update.callback_query.message.reply_text(f"Your mortal has not started the bot yet.")
        return ConversationHandler.END

    await update.callback_query.message.reply_text("Please type your message to your Mortal.")
    return MORTAL

# Send message to angel
async def send_angel(update: Update, context):
    username = update.message.chat.username.lower()
    angel_username = players[username].angel.username
    angel_chat_id = players[angel_username].chat_id

    if update.message.text:
        await context.bot.send_message(
            chat_id=angel_chat_id,
            text=f"🙇: {update.message.text}"
        )
    else:
        await send_non_text_message(update, context.bot, angel_chat_id)

    await update.message.reply_text("Your message has been sent to your Angel.")
    logger.info(f"{username} sent a message to their angel ({angel_username}).")

    return ConversationHandler.END

# Send message to mortal
async def send_mortal(update: Update, context):
    username = update.message.chat.username.lower()
    mortal_username = players[username].mortal.username
    mortal_chat_id = players[mortal_username].chat_id

    if update.message.text:
        await context.bot.send_message(
            chat_id=mortal_chat_id,
            text=f"😇: {update.message.text}"
        )
    else:
        await send_non_text_message(update, context.bot, mortal_chat_id)

    await update.message.reply_text("Your message has been sent to your Mortal.")
    logger.info(f"{username} sent a message to their mortal ({mortal_username}).")

    return ConversationHandler.END

# Command to cancel the conversation
async def cancel(update: Update, context):
    await update.message.reply_text("Message sending cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Main function to start the bot
def main():
    # Load the user data from the CSV file and set up pairings
    loadPlayers(players)

    # Set up bot token
    token = os.getenv("ANGEL_BOT_TOKEN")
    application = Application.builder().token(token).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))

    # Conversation handler for sending messages
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("send", send_command)],
        states={
            CHOOSING: [
                CallbackQueryHandler(start_angel, pattern="angel"),
                CallbackQueryHandler(start_mortal, pattern="mortal")
            ],
            ANGEL: [MessageHandler(filters.ALL & ~filters.COMMAND, send_angel)],
            MORTAL: [MessageHandler(filters.ALL & ~filters.COMMAND, send_mortal)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)

    # Start polling in a synchronous manner
    application.run_polling()

# Entry point of the script
if __name__ == '__main__':
    main()
