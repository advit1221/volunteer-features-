import discord
from discord.ext import commands
from discord import app_commands

from bot.core.logger import setup_logging
from config import Config


class MaximallyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents)
        self.logger = setup_logging("maximally")

    async def setup_hook(self) -> None:
        # Load cogs here if there were others
        try:
            from bot.cogs.volunteer import VolunteerCog

            await self.add_cog(VolunteerCog(self))
        except Exception as e:
            self.logger.error(f"Failed to load cogs: {e}")

        if Config.GUILD_ID:
            try:
                guild = discord.Object(id=int(Config.GUILD_ID))
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                self.logger.info("Synced commands to guild")
            except Exception as e:
                self.logger.error(f"Failed to sync commands: {e}")
        else:
            try:
                await self.tree.sync()
                self.logger.info("Synced global commands")
            except Exception as e:
                self.logger.error(f"Failed to sync global commands: {e}")


__all__ = ["MaximallyBot"]

