import discord
from discord.ext import commands

from src.utils import Color


class EmbedHelpCommand(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__()
        self.verify_checks = False
        self.no_category = "Other"


    async def send_pages(self):
        destination = self.get_destination()
        embed = discord.Embed(description="", color=Color.red())
        embed.set_thumbnail(url=self.context.bot.user.avatar_url)
        embed.set_author(name="Self-Bot for Discord")
        for page in self.paginator.pages:
            embed.description += page
        await destination.send(embed=embed)


    async def send_cog_help(self, cog):
        if getattr(cog, "hidden", False):
            return

        await super().send_cog_help(cog)
