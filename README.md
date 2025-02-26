# Angel and Mortal Bot

A Telegram bot for anonymous messaging between angels and mortals. This bot allows participants to send messages, media, and manage their profiles while maintaining anonymity.

## Features

- Anonymous messaging between angels and mortals
- User profiles with:
  - Customizable nicknames
  - Personal bios
  - Interests
- Rate limiting to prevent spam
- Support for multiple media types:
  - Photos
  - Videos
  - Voice messages
  - Video notes
  - Stickers
  - Animations (GIFs)
  - Audio files
  - Documents
- Persistent storage of chat IDs, player relationships, and user profiles

## Setup

1. Clone the repository:

```bash
git clone <https://github.com/felii30/angel-and-mortal-bot.git>
cd angel-and-mortal-bot
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:

```
ANGEL_BOT_TOKEN=your_telegram_bot_token
```

4. Set up your players data file (`data/players.csv`):

```csv
Player,Angel,Mortal
username1,username2,username3
username2,username3,username1
username3,username1,username2
```

5. Create necessary directories:

```bash
mkdir -p data logs
```

## Usage

1. Start the bot:

```bash
python -m src.bot
```

2. Available Commands:
   - `/start` - Start the bot and see available commands
   - `/send` - Send a message to your angel or mortal
   - `/setup` - Set up your profile (nickname, bio, interests)
   - `/profile` - View your profile and relationships
   - `/cancel` - Cancel any ongoing command

## Project Structure

```
angel-and-mortal-bot/
├── src/
│   ├── config/
│   │   └── config.py
│   ├── handlers/
│   │   └── command_handler.py
│   ├── models/
│   │   └── player.py
│   ├── services/
│   │   ├── message_service.py
│   │   ├── player_service.py
│   │   ├── profile_service.py
│   │   └── rate_limit_service.py
│   ├── utils/
│   │   └── database.py
│   └── bot.py
├── data/
│   ├── players.csv
│   └── chat_ids.json
├── logs/
├── requirements.txt
├── .env
└── README.md
```
