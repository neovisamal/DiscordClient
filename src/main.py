import tokenFinder, launch
import os

import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import utils

launch.launch()

TOKENS = tokenFinder.findTokens()
for token in TOKENS:
    os.system(f"python bot.py {token}")
    with open("log.txt") as file:
        if not file.read().endswith("Invalid token"):
            break
else:
    utils.raiseDialogue("You are not logged into the Discord app or discord.com website")
