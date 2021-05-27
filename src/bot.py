import discord
from discord.ext import commands

import sys

import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import utils


def main(TOKEN):
    bot = commands.Bot(command_prefix=".", self_bot=True)

    @bot.event
    async def on_ready():
        print("Logged into", bot.user)

    try:
        bot.run(TOKEN, bot=False)
    except discord.errors.LoginFailure:
        utils.log("Invalid token")


if __name__ == "__main__":
    main(sys.argv[1])
