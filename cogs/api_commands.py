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
        print(f"[Weather] Requête météo pour : {city}")
        try:
            weather_response, forecast_response = get_weather_json(city)
            location = weather_response.get("location", {})
            current = weather_response.get("current", {})
            forecast = forecast_response.get("forecast", {}).get("forecastday", [{}])[0]
            day = forecast.get("day", {})

            if not location or not current or not day:
                raise ValueError("Données météo incomplètes.")

            current_temp = current.get("temp_c", "?")
            condition = current.get("condition", {}).get("text", "?")
            icon_url = f"https:{current.get('condition', {}).get('icon', '')}" if current.get('condition', {}).get('icon') else None
            humidity = current.get("humidity", "?")
            wind_kph = current.get("wind_kph", "?")
            forecast_min = day.get("mintemp_c", "?")
            forecast_max = day.get("maxtemp_c", "?")

            embed = Embed(
                title=f"Météo pour {location.get('name', city)}",
                description=(
                    f"**Actuellement :** {current_temp}°C, {condition}\n"
                    f"**Prévision :** Min {forecast_min}°C, Max {forecast_max}°C\n"
                    f"**Humidité :** {humidity}%\n"
                    f"**Vent :** {wind_kph} km/h"
                ),
                color=0x1e90ff
            )
            if icon_url:
                embed.set_thumbnail(url=icon_url)
            embed.set_footer(text="Données fournies par WeatherAPI.com")

            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"[Weather] Erreur pour '{city}': {e}")
            await interaction.followup.send(
                f"❌ Impossible de récupérer la météo pour \"{city}\". Merci de vérifier le nom de la ville.\nDétail : {str(e)}",
                ephemeral=True,
            )


async def setup(bot):
    await bot.add_cog(ApiCommands(bot))
