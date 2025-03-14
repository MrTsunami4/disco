from typing import Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import discord
from discord import app_commands
from discord.ext import commands

from ui import DropdownView
from config import TIMEZONE


class BasicCommands(commands.Cog):
    """Basic bot commands."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def hello(self, interaction: discord.Interaction):
        """Says hello!"""
        await interaction.response.send_message(f"Hi, {interaction.user.mention}")

    @app_commands.command()
    @app_commands.describe(
        first_value="The first value you want to add something to",
        second_value="The value you want to add to the first value",
    )
    async def add(self, interaction: discord.Interaction, first_value: int, second_value: int):
        """Adds two numbers together."""
        await interaction.response.send_message(
            f"{first_value} + {second_value} = {first_value + second_value}"
        )

    @app_commands.command()
    @app_commands.rename(text_to_send="text")
    @app_commands.describe(text_to_send="Text to send in the current channel")
    async def send(self, interaction: discord.Interaction, text_to_send: str):
        """Sends the text into the current channel."""
        await interaction.response.send_message(text_to_send)
    
    @app_commands.command()
    async def color(self, interaction: discord.Interaction):
        """Sends a dropdown to select a color."""
        await interaction.response.send_message(view=DropdownView())

    @app_commands.command()
    @app_commands.describe(
        member="The member you want to get the joined date from; defaults to the user who uses the command"
    )
    async def joined(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ):
        """Says when a member joined."""
        member = member or interaction.user
        await interaction.response.send_message(
            f"{member} joined {discord.utils.format_dt(member.joined_at)}", ephemeral=True
        )
    
    @app_commands.command()
    async def midnight(self, interaction: discord.Interaction):
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
    
    @app_commands.command()
    async def best_language(self, interaction: discord.Interaction):
        """Sends the best programming language."""
        await interaction.response.send_message("The best programming language is Rust")

    @app_commands.context_menu(name="Show Join Date")
    async def show_join_date(self, interaction: discord.Interaction, member: discord.Member):
        """Context menu to show when a member joined."""
        await interaction.response.send_message(
            f"{member} joined at {discord.utils.format_dt(member.joined_at)}",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(BasicCommands(bot))