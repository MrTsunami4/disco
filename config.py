from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
GUILD_ID = int(getenv("GUILD_ID"))
TOKEN = getenv("DISCORD_TOKEN")
WEATHER_API_KEY = getenv("WEATHER_API_KEY")
GENERAL_CHANNEL_ID = int(getenv("GENERAL_CHANNEL_ID"))
TIMEZONE = "Europe/Paris"

# API endpoints
QUOTE_API_URL = "https://api.quotable.io/random"
TRANSLATE_API_URL = "https://translate.argosopentech.com/translate"
WEATHER_API_BASE_URL = "https://api.weatherapi.com/v1"

# Create guild object for commands
MY_GUILD = None  # Will be initialized in bot.py