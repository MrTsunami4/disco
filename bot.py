from os import getenv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Tuple, Dict, Any
from dotenv import load_dotenv
from asyncache import cached
from cachetools import TTLCache
import aiohttp

import discord
from discord import app_commands
from discord.ext import tasks


load_dotenv()

GUILD_ID = int(getenv("GUILD_ID"))
TOKEN = getenv("DISCORD_TOKEN")
WEATHER_API_KEY = getenv("WEATHER_API_KEY")
GENERAL_CHANNEL_ID = int(getenv("GENERAL_CHANNEL_ID"))
TIMEZONE = "Europe/Paris"

MY_GUILD = discord.Object(id=GUILD_ID)


def get_midnight_time():
    tt = datetime.now(ZoneInfo(TIMEZONE))
    md = tt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return md.timetz()


def embed_from_quote(my_quote: dict) -> discord.Embed:
    return discord.Embed(title="Quote", description=my_quote["content"]).set_author(
        name=my_quote["author"]
    )


class Dropdown(discord.ui.Select):
    def __init__(self):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(
                label="Red", description="Your favourite colour is red", emoji="🟥"
            ),
            discord.SelectOption(
                label="Green", description="Your favourite colour is green", emoji="🟩"
            ),
            discord.SelectOption(
                label="Blue", description="Your favourite colour is blue", emoji="🟦"
            ),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Choose your favourite colour...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(
            f"Your favourite colour is {self.values[0]}"
        )


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())


class MyClient(discord.Client):
    def __init__(self, *, client_intents: discord.Intents):
        super().__init__(intents=client_intents)
        self.tree = app_commands.CommandTree(self)
        self.session = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        self.tree.copy_global_to(guild=MY_GUILD)
        self.quote_task.start()
        await self.tree.sync(guild=MY_GUILD)

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

    @tasks.loop(time=get_midnight_time())
    async def quote_task(self):
        channel = self.get_channel(GENERAL_CHANNEL_ID)
        await channel.send("https://www.youtube.com/watch?v=F8jlpPVeTUg")

    @quote_task.before_loop
    async def before_quote_task(self):
        await self.wait_until_ready()


intents = discord.Intents.default()
client = MyClient(client_intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})\n------")


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f"Hi, {interaction.user.mention}")


@client.tree.command()
@app_commands.describe(
    first_value="The first value you want to add something to",
    second_value="The value you want to add to the first value",
)
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    await interaction.response.send_message(
        f"{first_value} + {second_value} = {first_value + second_value}"
    )


@client.tree.command()
@app_commands.rename(text_to_send="text")
@app_commands.describe(text_to_send="Text to send in the current channel")
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends the text into the current channel."""
    await interaction.response.send_message(text_to_send)


@client.tree.command()
@app_commands.describe(
    member="The member you want to get the joined date from; defaults to the user who uses the "
    "command"
)
async def joined(
    interaction: discord.Interaction, member: Optional[discord.Member] = None
):
    """Says when a member joined."""
    member = member or interaction.user
    await interaction.response.send_message(
        f"{member} joined {discord.utils.format_dt(member.joined_at)}", ephemeral=True
    )


@client.tree.context_menu(name="Show Join Date")
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(
        f"{member} joined at {discord.utils.format_dt(member.joined_at)}",
        ephemeral=True,
    )


@client.tree.context_menu(name="Translate")
async def translate(interaction: discord.Interaction, message: discord.Message):
    """Translate text to another language."""
    await interaction.response.defer(ephemeral=True)
    try:
        async with client.session.post(
            "https://translate.argosopentech.com/translate",
            json={"q": message.content, "source": "fr", "target": "en"},
            timeout=30,
        ) as response:
            if response.status != 200:
                raise ValueError(
                    f"Translation request failed with status {response.status}"
                )
            data = await response.json()
            translated_text = data.get("translatedText")
            if not translated_text:
                raise ValueError("Translation failed")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
    else:
        await interaction.followup.send(
            f"Translated text: {translated_text}", ephemeral=True
        )


@client.tree.command()
async def quote(interaction: discord.Interaction):
    """Sends a random quote."""
    try:
        async with client.session.get(
            "https://api.quotable.io/random?maxLength=230"
        ) as response:
            if response.status == 200:
                my_quote = await response.json()
                await interaction.response.send_message(
                    embed=embed_from_quote(my_quote)
                )
            else:
                await interaction.response.send_message(
                    "Failed to fetch a quote", ephemeral=True
                )
    except Exception as e:
        await interaction.response.send_message(
            f"An error occurred: {e}", ephemeral=True
        )


@cached(cache=TTLCache(maxsize=128, ttl=600))
async def get_weather_json(city: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Get weather data for a city with caching."""
    weather_url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
    forecast_url = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&aqi=no&alerts=no"

    try:
        async with (
            client.session.get(weather_url) as weather_response,
            client.session.get(forecast_url) as forecast_response,
        ):
            if weather_response.status != 200 or forecast_response.status != 200:
                raise ValueError(
                    f"Weather API error: status codes {weather_response.status}, {forecast_response.status}"
                )

            return await weather_response.json(), await forecast_response.json()
    except Exception as e:
        raise ValueError(f"Failed to get weather data: {e}")


@client.tree.command()
@app_commands.describe(city="The city you want to get the weather for")
async def weather(interaction: discord.Interaction, city: str):
    """Get the current weather and forecast for a city."""
    await interaction.response.defer()

    try:
        weather_response, forecast_response = await get_weather_json(city)

        current_temp = weather_response["current"]["temp_c"]
        condition = weather_response["current"]["condition"]["text"]
        forecast = forecast_response["forecast"]["forecastday"][0]
        forecast_min = forecast["day"]["mintemp_c"]
        forecast_max = forecast["day"]["maxtemp_c"]

        embed = discord.Embed(
            title=f"Weather for {weather_response['location']['name']}",
            description=(
                f"**Current:** {current_temp}°C, {condition}\n"
                f"**Forecast:** Min: {forecast_min}°C, Max: {forecast_max}°C"
            ),
            color=0x3498DB,
        )
        embed.set_footer(text="Data from WeatherAPI.com")

        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(
            f'Error: Could not retrieve weather data for "{city}"\n{str(e)}',
            ephemeral=True,
        )


@client.tree.command()
async def midnight(interaction: discord.Interaction):
    """Tell the time until midnight."""
    now = datetime.now(ZoneInfo(TIMEZONE))
    midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    time_until_midnight = midnight - now
    hours, remainder = divmod(time_until_midnight.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    await interaction.response.send_message(
        f"Time until midnight: {hours}h {minutes}m {seconds}s"
    )


@client.tree.command()
async def best_language(interaction: discord.Interaction):
    """Sends the best programming language."""
    await interaction.response.send_message("The best programming language is Rust")


@client.tree.command()
async def color(interaction: discord.Interaction):
    """Sends a random color."""
    await interaction.response.send_message(view=DropdownView())


if __name__ == "__main__":
    client.run(TOKEN)
