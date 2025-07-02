# Disco Discord Bot

A modular Discord bot with various commands and features.

## Project Structure

```
├── bot.py                # Main entry point
├── config.py             # Configuration settings
├── utils.py              # Utility functions
├── ui.py                 # Discord UI components
├── requirements.txt      # Python dependencies
├── launch.sh             # Launch script
├── disco.service         # Systemd service file
└── cogs/                 # Command modules
    ├── api_commands.py   # API-related commands
    ├── basic_commands.py # Basic bot commands
    └── user_commands.py  # User-related commands
```

## Setup

1. Create a `.env` file in the project root with:

```
DISCORD_TOKEN=your_bot_token
GUILD_ID=your_guild_id
GENERAL_CHANNEL_ID=your_channel_id
WEATHER_API_KEY=your_weather_api_key
```

2. Install [uv](https://docs.astral.sh/uv/)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Run the bot:

```bash
uv run bot.py
```

## Commands

### Basic Commands

- `/hello`: Says hello
- `/add`: Adds two numbers
- `/send`: Sends text to the channel
- `/color`: Shows color selection dropdown
- `/joined`: Shows when a member joined
- `/midnight`: Shows time until midnight
- `/best_language`: Shows the best programming language

### API Commands

- `/quote`: Shows a random quote
- `/weather`: Shows weather for a specified city
- Context menu `Translate`: Translates a message from French to English

### User Commands

- Context menu `Show Message Count`: Shows how many messages a user has sent

## Service Installation

To run as a system service:

1. Edit `disco.service` to point to the correct directories
2. Copy to systemd:

```bash
sudo cp disco.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable disco.service
sudo systemctl start disco.service
```

To restart the service:

```bash
sudo systemctl restart disco.service
```

## Adding New Commands

To add new commands, create a new Python file in the `cogs` directory following the pattern of existing cogs, then restart the bot.
