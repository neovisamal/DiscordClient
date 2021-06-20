import discord
from discord.ext import commands

from src.utils import Color

import traceback


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def bot_check(self, ctx):
        if ctx.command.name != "setup":
            raise commands.BadArgument("Self-Bot must be setup with .setup")
        else:
            return True


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            message = "Self-Bot must be setup with .setup"

        elif isinstance(error, commands.BadArgument):
            message = error

        else:
            message = "Something went wrong!!"
            traceback.print_tb(error.__traceback__)
            print(type(error), error)

        embed = discord.Embed(title=message, color=Color.red())
        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Setup(bot))
