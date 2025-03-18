import discord
from discord import app_commands
from discord.ext import commands

from utils import count_user_messages


class UserCommands(commands.Cog):
    """Commands related to Discord users."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.context_menu(name="Show Message Count")
    async def show_message_count(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        """Show the number of messages sent by a user on the server."""
        await interaction.response.defer(ephemeral=True)

        try:
            message_count = await count_user_messages(
                interaction.guild.id,
                member.id,
                interaction.guild.text_channels,
                interaction.guild.me,
            )
            await interaction.followup.send(
                f"{member.display_name} has sent {message_count} messages on this server.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"An error occurred while counting messages: {e}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(UserCommands(bot))
