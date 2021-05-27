import tokenFinder
import discord
from discord.ext import commands
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=".", self_bot=True)


    async def on_ready(self):
        print("Logged into", self.user)


def main():
    tokens = tokenFinder.findTokens()
    loop = asyncio.get_event_loop()
    for token in tokens:
        bot = Bot()
        try:
            loop.create_task(bot.start(token, bot=False))
            break
        except:
            pass
    else:
        print("No tokens found")
    loop.run_forever()

main()
