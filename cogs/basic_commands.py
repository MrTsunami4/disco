from typing import Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from discord import Interaction, Member, app_commands
from discord.utils import format_dt
from discord.ext.commands import Cog

from ui import DropdownView
from config import TIMEZONE
from utils import get_midnight_time_aware

class BasicCommands(Cog):
    """Basic bot commands."""

    def __init__(self, bot):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Show Join Date",
            callback=self.show_join_date,
        )
        self.bot.tree.add_command(self.ctx_menu)

    def get_midnight_time_corrected(self):
        """Calculate the time for midnight of the minus the bot latency."""
        now = datetime.now(ZoneInfo(TIMEZONE)) - timedelta(seconds=self.bot.latency)
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return midnight.timetz()

    @app_commands.command()
    async def hello(self, interaction: Interaction):
        """Says hello!"""
        await interaction.response.send_message(f"Hi, {interaction.user.mention}")

    @app_commands.command()
    @app_commands.describe(
        first_value="The first value you want to add something to",
        second_value="The value you want to add to the first value",
    )
    async def add(self, interaction: Interaction, first_value: int, second_value: int):
        """Adds two numbers together."""
        await interaction.response.send_message(
            f"{first_value} + {second_value} = {first_value + second_value}"
        )

    @app_commands.command()
    async def send(self, interaction: Interaction, text_to_send: str):
        """Sends the text into the current channel."""
        await interaction.response.send_message(text_to_send)

    @app_commands.command()
    async def color(self, interaction: Interaction):
        """Sends a dropdown to select a color."""
        await interaction.response.send_message(view=DropdownView())

    @app_commands.command()
    @app_commands.describe(
        member="The member you want to get the joined date from; defaults to the user who uses the command"
    )
    async def joined(self, interaction: Interaction, member: Optional[Member] = None):
        """Says when a member joined."""
        member = member or interaction.user
        await interaction.response.send_message(
            f"{member.mention} joined {format_dt(member.joined_at)},",
            silent=True,
        )

    @app_commands.command()
    async def midnight(self, interaction: Interaction):
        """Tell the time until midnight."""
        now = datetime.now(ZoneInfo(TIMEZONE))
        time_until_midnight = get_midnight_time_aware() - now
        hours, remainder = divmod(time_until_midnight.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        await interaction.response.send_message(
            f"Time until midnight: {hours}h {minutes}m {seconds}s"
        )

    @app_commands.command()
    async def ping(self, interaction: Interaction):
        """Pings the bot."""
        await interaction.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms")

    @app_commands.command()
    async def midnight_without_delay(self, interaction: Interaction):
        """Sends the time until midnight without delay."""
        now = datetime.now(ZoneInfo(TIMEZONE)) - timedelta(seconds=self.bot.latency)
        time_until_midnight = get_midnight_time_aware() - now
        hours, remainder = divmod(time_until_midnight.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        await interaction.response.send_message(
            f"Time until midnight without delay: {hours}h {minutes}m {seconds}s"
        )

    @app_commands.command()
    async def best_language(self, interaction: Interaction):
        """Sends the best programming language."""
        await interaction.response.send_message("The best programming language is Rust")

    async def show_join_date(self, interaction: Interaction, member: Member):
        """Context menu to show when a member joined."""
        await interaction.response.send_message(
            f"{member.mention} joined at {format_dt(member.joined_at)}",
            silent=True,
        )

    
async def setup(bot):
    await bot.add_cog(BasicCommands(bot))
