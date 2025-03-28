from discord import Embed, Interaction, Message, app_commands
from discord.ext.commands import Cog
from requests import RequestException, get, post

from config import QUOTE_API_URL, TRANSLATE_API_URL
from utils import embed_from_quote, get_weather_json


class ApiCommands(Cog):
    """Commands that interact with external APIs."""

    def __init__(self, bot):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Translate",
            callback=self.translate,
        )
        self.bot.tree.add_command(self.ctx_menu)

    @app_commands.command()
    async def quote(self, interaction: Interaction):
        """Sends a random quote."""
        await interaction.response.defer(ephemeral=True)

        try:
            response = get(f"{QUOTE_API_URL}?maxLength=230")
            response.raise_for_status()
            my_quote = await response.json()
            await interaction.followup.send(embed=embed_from_quote(my_quote))

        except RequestException as e:
            await interaction.response.send_message(
                f"Failed to get a quote: {e}", ephemeral=True
            )

    @app_commands.command()
    @app_commands.describe(city="The city you want to get the weather for")
    async def weather(self, interaction: Interaction, city: str):
        """Get the current weather and forecast for a city."""
        await interaction.response.defer()

        try:
            weather_response, forecast_response = get_weather_json(city)

            current_temp = weather_response["current"]["temp_c"]
            forecast = forecast_response["forecast"]["forecastday"][0]
            forecast_min = forecast["day"]["mintemp_c"]
            forecast_max = forecast["day"]["maxtemp_c"]

            embed = Embed(
                title=f"Weather for {weather_response['location']['name']}",
                description=(
                    f"**Current:** {current_temp}°C\n"
                    f"**Forecast:** Min: {forecast_min}°C, Max: {forecast_max}°C"
                ),
            )
            embed.set_footer(text="Data from WeatherAPI.com")

            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(
                f'Error: Could not retrieve weather data for "{city}"\n{str(e)}',
                ephemeral=True,
            )

    async def translate(self, interaction: Interaction, message: Message):
        """Translate text from French to English."""
        await interaction.response.defer()
        try:
            response = post(
                TRANSLATE_API_URL,
                json={"q": message.content, "source": "fr", "target": "en"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            translated_text = data.get("translatedText")
            if not translated_text:
                raise ValueError("Translation failed")
            await interaction.followup.send(translated_text)
        except RequestException as e:
            await interaction.followup.send(
                f"Failed to translate text: {e}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(ApiCommands(bot))
