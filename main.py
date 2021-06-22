from src.tokenFinder import TokenFinder
from src.bot import Bot
import src.utils as utils
from src.help import EmbedHelpCommand

import discord
import json
import asyncio

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="Boots the bot into Debug mode, where only the bot Owner can use commands and tracebacks are printed etc", action="store_true")
parser.add_argument("-w", "--windows", help="Changes the asyncio loop policy to WindowsSelectorEventLoopPolicy", action="store_true")
args = parser.parse_args()

if args.windows:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def new_login():
<<<<<<< HEAD
    TOKENS = TokenFinder().to_list()
=======
    TOKENS = TokenFinder()
>>>>>>> master
    if not TOKENS:
        utils.raiseDialogue("Could not detect your Discord token! Your token is required to run a Self-Bot.")
        exit()


    for token in TOKENS:
        asyncio.set_event_loop(asyncio.new_event_loop())
        bot = Bot(command_prefix=Bot.determine_prefix, case_insensitive=True, self_bot=True, help_command=EmbedHelpCommand(), allowed_mentions=discord.AllowedMentions.none(), debug=args.debug)
        res = bot.run(token, bot=False)
        if res != False:
            exit()


try:
    bot = Bot(command_prefix=Bot.determine_prefix, case_insensitive=True, self_bot=True, help_command=EmbedHelpCommand(), allowed_mentions=discord.AllowedMentions.none(), intents=discord.Intents.all(), debug=args.debug)
    res = bot.run(bot.config.TOKEN)
    if not res:
        new_login()
except (FileNotFoundError, TypeError):
    new_login()
