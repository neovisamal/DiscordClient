from src.tokenFinder import findTokens
from src.bot import Bot
import src.utils as utils

import json
import asyncio

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("TOKEN", help="The variable name for the token to log into a Discord client")
parser.add_argument("-d", "--debug", help="Boots the bot into Debug mode, where only the bot Owner can use commands and tracebacks are printed etc", action="store_true")
parser.add_argument("-w", "--windows", help="Changes the asyncio loop policy to WindowsSelectorEventLoopPolicy", action="store_true")
args = parser.parse_args()

if args.windows:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def new_login():
    TOKENS = findTokens()
    if not TOKENS:
        utils.raiseDialogue("Could not detect your Discord token! Your token is required to run a Self-Bot.")
        exit()


    for token in TOKENS:
        asyncio.set_event_loop(asyncio.new_event_loop())
        bot = Bot()
        res = bot.run(token, bot=False)
        if res != False:
            exit()


try:
    bot = Bot()
    res = bot.run(bot.config.TOKEN)
    if not res:
        new_login()
except (FileNotFoundError, TypeError):
    new_login()
