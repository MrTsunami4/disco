from os import listdir
from discord import Intents
from discord.ext import commands, tasks


import config
from utils import get_midnight_time, get_server_delay, midnight_without_delay, one_min_before_midnight, ten_pm_time, midnight


class DiscoBot(commands.Bot):
    """Main Discord bot class with improved organization."""

    def __init__(self):
        intents = Intents.default()
        super().__init__(command_prefix=config.PREFIX, intents=intents)

    async def setup_hook(self):
        """Sets up the bot with required configurations."""

        global midnight
        if midnight is None:
            get_midnight_time()

        # Start scheduled tasks
        self.midnight_task.start()
        self.one_min_before_midnight_task.start()
        self.ten_pm_task.start()

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

    @tasks.loop(time=ten_pm_time())
    async def ten_pm_task(self):
        """Run the midnight function to redefine midnight time."""
        get_midnight_time()

    @tasks.loop(time=one_min_before_midnight())
    async def one_min_before_midnight_task(self):
        """Get the server delay one minute before midnight."""
        get_server_delay()

    @tasks.loop(time=midnight_without_delay())
    async def midnight_task(self):
        """Task that runs at midnight."""
        channel = self.get_channel(config.GENERAL_CHANNEL_ID)
        if channel:
            await channel.send("https://www.youtube.com/watch?v=aES3XaSD9wc")

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
