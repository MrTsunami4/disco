from discord import Embed, Interaction, app_commands
from discord.ext.commands import Cog

from utils import get_weather_json


class ApiCommands(Cog):
    """Commands that interact with external APIs."""

    def __init__(self, bot):
        self.bot = bot

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


async def setup(bot):
    await bot.add_cog(ApiCommands(bot))
