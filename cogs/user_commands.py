from discord import app_commands, Interaction, Member
from discord.ext.commands import Cog

from utils import count_user_messages


class UserCommands(Cog):
    """Commands related to Discord users."""

    def __init__(self, bot):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Show Message Count",
            callback=self.show_message_count,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def show_message_count(self, interaction: Interaction, member: Member):
        """Show the number of messages sent by a user on the server."""
        await interaction.response.defer(ephemeral=True)

        try:
            message_count = await count_user_messages(
                interaction.guild,
                member.id,
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
