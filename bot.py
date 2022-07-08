import os
import datetime
from typing import Optional
from dotenv import load_dotenv
import requests

import discord
from discord import app_commands
from discord.ext import tasks

load_dotenv()

GUILD_ID = int(os.getenv("GUILD_ID"))
TOKEN = os.getenv("DISCORD_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GENERAL_CHANNEL_ID = int(os.getenv("GENERAL_CHANNEL_ID"))

MY_GUILD = discord.Object(id=GUILD_ID)

tz = datetime.timezone(datetime.timedelta(hours=+1))

when = datetime.time(hour=0, minute=0, tzinfo=tz)


def embed_from_quote(quote: dict):
    embed = discord.Embed(title="Quote")
    embed.description = quote['content']
    embed.set_author(name=quote['author'])
    return embed


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        self.quote_task.start()
        await self.tree.sync(guild=MY_GUILD)

    @tasks.loop(time=when)
    async def quote_task(self):
        channel = self.get_channel(GENERAL_CHANNEL_ID)
        response = requests.get("https://api.quotable.io/random?maxLength=230")
        quote = response.json()
        await channel.send(embed=embed_from_quote(quote))

    @quote_task.before_loop
    async def before_quote_task(self):
        await self.wait_until_ready()


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


@client.tree.command()
@app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value',
)
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')


@client.tree.command()
@app_commands.rename(text_to_send='text')
@app_commands.describe(text_to_send='Text to send in the current channel')
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends the text into the current channel."""
    await interaction.response.send_message(text_to_send)


@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Says when a member joined."""
    member = member or interaction.user
    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


@client.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')


@client.tree.command()
async def quote(interaction: discord.Interaction):
    """Sends a random quote."""
    response = requests.get('https://api.quotable.io/random?maxLength=230')
    quote = response.json()
    await interaction.response.send_message(embed=embed_from_quote(quote))


@client.tree.command()
@app_commands.describe(city='The city you want to get the weather for')
async def weather(interaction: discord.Interaction, city: str):
    """Get the current weather"""
    try:
        response = requests.get(
            f'http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no')
        response.raise_for_status()
        second_response = requests.get(
            f'http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&aqi=no&alerts=no')
        second_response.raise_for_status()
    except Exception as e:
        await interaction.response.send_message("Something went wrong, please try again")
        return
    current_temp = response.json()['current']['temp_c']
    forecast = second_response.json()['forecast']['forecastday'][0]
    forecast_min = forecast['day']['mintemp_c']
    forecast_max = forecast['day']['maxtemp_c']
    embed = discord.Embed(title="Weather")
    embed.description = f'Current temperature: {current_temp}°C\n' f'Forecast: Min: {forecast_min}°C, Max: {forecast_max}°C'
    await interaction.response.send_message(embed=embed)

client.run(TOKEN)
