import tokenFinder
import os

import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TOKENS = tokenFinder.findTokens()
for token in TOKENS:
    os.system(f"python bot.py {token}")
