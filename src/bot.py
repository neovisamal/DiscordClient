import discord
from discord.ext import commands
import os
from help import EmbedHelpCommand


class Bot(commands.Bot):
    def __init__(bot):
        super().__init__(command_prefix=".", self_bot=True, help_command=EmbedHelpCommand())
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                fileName = file[:-3]
                bot.load_extension(f"cogs.{fileName}")


    async def on_ready(bot):
        print("Logged into", bot.user)
