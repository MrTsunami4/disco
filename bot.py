from os import getenv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Iterator, Optional
from dotenv import load_dotenv
from asyncache import cached
from cachetools import TTLCache
from requests import get, post

import discord
from discord import app_commands
from discord.ext import tasks

from helper import nth_element

load_dotenv()

GUILD_ID = int(getenv("GUILD_ID"))
TOKEN = getenv("DISCORD_TOKEN")
WEATHER_API_KEY = getenv("WEATHER_API_KEY")
GENERAL_CHANNEL_ID = int(getenv("GENERAL_CHANNEL_ID"))

MY_GUILD = discord.Object(id=GUILD_ID)


tt = datetime.now(ZoneInfo("Europe/Paris"))
md = tt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
mid = md.timetz()


def embed_from_quote(my_quote: dict):
    embed = discord.Embed(title="Quote")
    embed.description = my_quote["content"]
    embed.set_author(name=my_quote["author"])
    return embed


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

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        self.quote_task.start()
        await self.tree.sync(guild=MY_GUILD)

    @tasks.loop(time=mid)
    async def quote_task(self):
        channel = self.get_channel(GENERAL_CHANNEL_ID)
        # response = get("https://api.quotable.io/random?maxLength=230")
        # my_quote = response.json()
        # await channel.send(embed=embed_from_quote(my_quote))
        await channel.send("https://www.youtube.com/watch?v=F8jlpPVeTUg")

    @quote_task.before_loop
    async def before_quote_task(self):
        await self.wait_until_ready()


intents = discord.Intents.default()
client = MyClient(client_intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


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
    await interaction.response.defer(ephemeral=True)
    """Translate text to another language."""
    try:
        response = post(
            "https://translate.argosopentech.com/translate",
            json={"q": message.content, "source": "fr", "target": "en"},
            timeout=30,
        )
        response.raise_for_status()
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
        return
    try:
        json = response.json()
        translated_text = json["translatedText"]
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
        return
    await interaction.followup.send(
        f"Translated text: {translated_text}", ephemeral=True
    )


@client.tree.command()
async def quote(interaction: discord.Interaction):
    """Sends a random quote."""
    response = get("https://api.quotable.io/random?maxLength=230")
    my_quote = response.json()
    await interaction.response.send_message(embed=embed_from_quote(my_quote))


@cached(cache=TTLCache(maxsize=1024, ttl=600))
async def get_weather_json(city: str):
    try:
        weather_response = get(
            f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
        )
        weather_response.raise_for_status()
        forecast_response = get(
            f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&aqi=no&alerts=no"
        )
        forecast_response.raise_for_status()
    except Exception as e:
        raise e
    return weather_response.json(), forecast_response.json()


@client.tree.command()
@app_commands.describe(city="The city you want to get the weather for")
async def weather(interaction: discord.Interaction, city: str):
    """Get the current weather"""
    try:
        weather_response, forecast_response = await get_weather_json(city)
    except Exception as _e:
        await interaction.response.send_message(
            f'Error: the city "{city}" was not found', ephemeral=True
        )
        return
    current_temp = weather_response["current"]["temp_c"]
    forecast = forecast_response["forecast"]["forecastday"][0]
    forecast_min = forecast["day"]["mintemp_c"]
    forecast_max = forecast["day"]["maxtemp_c"]
    embed = discord.Embed(title="Weather")
    embed.description = (
        f"Current temperature: {current_temp}°C\n"
        f"Forecast: Min: {forecast_min}°C, Max: {forecast_max}°C "
    )
    await interaction.response.send_message(embed=embed)


# A command tha tell the time until midnight
@client.tree.command()
async def midnight(interaction: discord.Interaction):
    """Sends the time until midnight."""
    paris_dt = datetime.now(ZoneInfo("Europe/Paris"))
    midnight = paris_dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(
        days=1
    )
    time_until_midnight = midnight - paris_dt
    await interaction.response.send_message(
        f"Time until midnight: {time_until_midnight}"
    )


# A command that say what the best programming language is
@client.tree.command()
async def best_language(interaction: discord.Interaction):
    """Sends the best programming language."""
    await interaction.response.send_message("The best programming language is Rust")


@client.tree.command()
async def color(interaction: discord.Interaction):
    """Sends a random color."""
    await interaction.response.send_message(view=DropdownView())


def fibo_gen() -> Iterator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def fib(n: int) -> int:
    return nth_element(fibo_gen(), n)


# @client.tree.command()
# async def fibonacci(interaction: discord.Interaction, n: int):
#     """Sends the nth fibonacci number."""
#     await interaction.response.send_message(f'{n}th fibonacci number is {fib(n)}')


@client.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    await channel.send(f"Welcome {member.mention} to {guild.name}!")


if __name__ == "__main__":
    client.run(TOKEN)
