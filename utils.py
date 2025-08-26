from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from asyncache import cached
from cachetools import TTLCache
from discord import Embed, Guild
from discord.errors import Forbidden
from requests import get
from requests.exceptions import RequestException
from discord.utils import utcnow, time_snowflake, snowflake_time


from config import ADMIN_ID, TIMEZONE, WEATHER_API_KEY, WEATHER_API_BASE_URL

def get_midnight_time():
    """Calculate the time for midnight of the next day."""
    from zoneinfo import ZoneInfo

    current_time = datetime.now(ZoneInfo(TIMEZONE))
    midnight = current_time.replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)
    return midnight.timetz()


def embed_from_quote(quote_data: dict) -> Embed:
    """Create a Discord embed from quote data."""
    return Embed(title="Quote", description=quote_data["content"]).set_author(
        name=quote_data["author"]
    )


@cached(cache=TTLCache(maxsize=128, ttl=600))
def get_weather_json(city: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Get weather data for a city with caching."""

    weather_url = (
        f"{WEATHER_API_BASE_URL}/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
    )
    forecast_url = f"{WEATHER_API_BASE_URL}/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&aqi=no&alerts=no"

    try:
        weather_response = get(weather_url)
        weather_response.raise_for_status()

        forecast_response = get(forecast_url)
        forecast_response.raise_for_status()

        return weather_response.json(), forecast_response.json()
    except RequestException as e:
        raise ValueError(f"Failed to get weather data: {e}")


@cached(cache=TTLCache(maxsize=200, ttl=3600))  # Cache for 1 hour
async def count_user_messages_in_last_24_hours(
    guild: Guild,
    user_id: int,
) -> int:
    """Count the number of messages from a user in a guild with caching."""
    message_count = 0

    twenty_four_hours_ago = datetime.now() - timedelta(days=1)

    channels = guild.text_channels
    guild_me = guild.me

    for channel in channels:
        if not channel.permissions_for(guild_me).read_message_history:
            continue

        try:
            async for message in channel.history(
                limit=None, after=twenty_four_hours_ago
            ):
                if message.author.id == user_id:
                    message_count += 1
        except (Forbidden, Exception) as e:
            # Ignore permission errors and other exceptions
            if not isinstance(e, Forbidden):
                print(f"Error counting messages in {channel.name}: {e}")

    return message_count


def is_admin(user_id: int) -> bool:
    """Check if a user is an admin."""
    return user_id == ADMIN_ID

