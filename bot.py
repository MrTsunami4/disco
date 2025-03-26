from os import listdir
from discord import Intents
from discord.ext import commands, tasks


import config
from utils import get_midnight_time


class DiscoBot(commands.Bot):
    """Main Discord bot class with improved organization."""

    def __init__(self):
        intents = Intents.default()
        super().__init__(command_prefix=config.PREFIX, intents=intents)

    async def setup_hook(self):
        """Sets up the bot with required configurations."""

        # Start scheduled tasks
        self.midnight_task.start()

        # Load all cogs
        await self.load_extensions()

        # Sync application commands
        self.tree.copy_global_to(guild=config.MY_GUILD)
        await self.tree.sync(guild=config.MY_GUILD)

    async def load_extensions(self):
        """Load all cog extensions."""
        for filename in listdir("./cogs"):
            if filename.endswith(".py"):
                extension = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(extension)
                    print(f"Loaded extension: {extension}")
                except Exception as e:
                    print(f"Failed to load extension {extension}: {e}")

    @tasks.loop(time=get_midnight_time())
    async def midnight_task(self):
        """Task that runs at midnight."""
        channel = self.get_channel(config.GENERAL_CHANNEL_ID)
        if channel:
            await channel.send("https://www.youtube.com/watch?v=F8jlpPVeTUg")

    @midnight_task.before_loop
    async def before_midnight_task(self):
        """Wait until the bot is ready before starting the task."""
        await self.wait_until_ready()


bot = DiscoBot()


@bot.event
async def on_ready():
    """Called when the bot is ready."""
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


if __name__ == "__main__":
    bot.run(config.TOKEN)
