from os import getenv
from discord import Object
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
_guild_id = getenv("GUILD_ID")
if _guild_id is None:
    raise ValueError("GUILD_ID environment variable is not set")
GUILD_ID = int(_guild_id)
TOKEN = getenv("DISCORD_TOKEN")
WEATHER_API_KEY = getenv("WEATHER_API_KEY")
_general_channel_id = getenv("GENERAL_CHANNEL_ID")
if _general_channel_id is None:
    raise ValueError("GENERAL_CHANNEL_ID environment variable is not set")
GENERAL_CHANNEL_ID = int(_general_channel_id)
TIMEZONE = "Europe/Paris"
PREFIX = "%"
_admin_id = getenv("ADMIN_ID")
if _admin_id is None:
    raise ValueError("ADMIN_ID environment variable is not set")
ADMIN_ID = int(_admin_id)

# API endpoints
QUOTE_API_URL = "https://api.quotable.io/random"
TRANSLATE_API_URL = "https://translate.argosopentech.com/translate"
WEATHER_API_BASE_URL = "https://api.weatherapi.com/v1"

# Create guild object for commands
MY_GUILD = Object(id=GUILD_ID)
