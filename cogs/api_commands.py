import discord
from discord import app_commands
from discord.ext import commands

from config import QUOTE_API_URL, TRANSLATE_API_URL
from utils import embed_from_quote, get_weather_json


class ApiCommands(commands.Cog):
    """Commands that interact with external APIs."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def quote(self, interaction: discord.Interaction):
        """Sends a random quote."""
        try:
            async with self.bot.session.get(
                f"{QUOTE_API_URL}?maxLength=230"
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

    @app_commands.command()
    @app_commands.describe(city="The city you want to get the weather for")
    async def weather(self, interaction: discord.Interaction, city: str):
        """Get the current weather and forecast for a city."""
        await interaction.response.defer()

        try:
            weather_response, forecast_response = await get_weather_json(
                self.bot.session, city
            )

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

    @app_commands.context_menu(name="Translate")
    async def translate(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        """Translate text from French to English."""
        await interaction.response.defer(ephemeral=True)
        try:
            async with self.bot.session.post(
                TRANSLATE_API_URL,
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


async def setup(bot):
    await bot.add_cog(ApiCommands(bot))
