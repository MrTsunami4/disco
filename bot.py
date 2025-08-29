from datetime import timedelta
from os import listdir
from discord import Intents, TextChannel
from discord.ext import commands, tasks
from discord.utils import sleep_until


import config
from utils import get_midnight_time, get_midnight_time_corrected


class DiscoBot(commands.Bot):
    """Main Discord bot class with improved organization."""

    instance = None  # Class variable to hold the singleton instance

    def __init__(self):
        intents = Intents.default()
        super().__init__(command_prefix=config.PREFIX, intents=intents)
        global instance
        if DiscoBot.instance is None:
            DiscoBot.instance = self

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

    @tasks.loop()
    async def midnight_task(self):
        """Task that runs at midnight."""
        just_before_midnight = get_midnight_time() - timedelta(minutes=1)
        await sleep_until(just_before_midnight)
        midnight_time = get_midnight_time_corrected(self)
        await sleep_until(midnight_time)
        channel = self.get_channel(config.GENERAL_CHANNEL_ID)
        if isinstance(channel, TextChannel):
            await channel.send("https://www.youtube.com/watch?v=aES3XaSD9wc")

    @midnight_task.before_loop
    async def before_midnight_task(self):
        """Wait until the bot is ready before starting the task."""
        await self.wait_until_ready()


bot = DiscoBot()


@bot.event
async def on_ready():
    """Called when the bot is ready."""
    if bot.user is not None:
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    else:
        print("Logged in, but bot user is None.")
    print("------")


if __name__ == "__main__":
    if config.TOKEN is None:
        raise ValueError(
            "Discord bot token (config.TOKEN) is None. Please set a valid token in your config."
        )
    bot.run(config.TOKEN)
