from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from asyncache import cached
from cachetools import TTLCache
import discord
import aiohttp

from config import TIMEZONE, WEATHER_API_KEY, WEATHER_API_BASE_URL


def get_midnight_time():
    """Calculate the time for midnight of the next day."""
    from zoneinfo import ZoneInfo
    tt = datetime.now(ZoneInfo(TIMEZONE))
    md = tt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return md.timetz()


def embed_from_quote(quote_data: dict) -> discord.Embed:
    """Create a Discord embed from quote data."""
    return discord.Embed(title="Quote", description=quote_data["content"]).set_author(
        name=quote_data["author"]
    )


@cached(cache=TTLCache(maxsize=128, ttl=600))
async def get_weather_json(session: aiohttp.ClientSession, city: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Get weather data for a city with caching."""
    weather_url = f"{WEATHER_API_BASE_URL}/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
    forecast_url = f"{WEATHER_API_BASE_URL}/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&aqi=no&alerts=no"

    try:
        async with (
            session.get(weather_url) as weather_response,
            session.get(forecast_url) as forecast_response,
        ):
            if weather_response.status != 200 or forecast_response.status != 200:
                raise ValueError(
                    f"Weather API error: status codes {weather_response.status}, {forecast_response.status}"
                )

            return await weather_response.json(), await forecast_response.json()
    except Exception as e:
        raise ValueError(f"Failed to get weather data: {e}")


@cached(cache=TTLCache(maxsize=200, ttl=86400))  # Cache for 1 day
async def count_user_messages(
    guild_id: int,
    user_id: int,
    channels: list[discord.TextChannel],
    guild_me: discord.Member,
) -> int:
    """Count the number of messages from a user in a guild with caching."""
    message_count = 0

    for channel in channels:
        if not channel.permissions_for(guild_me).read_message_history:
            continue

        try:
            async for _ in channel.history(limit=None, user=discord.Object(id=user_id)):
                message_count += 1
        except (discord.errors.Forbidden, Exception) as e:
            # Ignore permission errors and other exceptions
            if not isinstance(e, discord.errors.Forbidden):
                print(f"Error counting messages in {channel.name}: {e}")

    return message_count