from utils import *

import discord
from discord.ext import commands

from PyDictionary import PyDictionary
from spellchecker import SpellChecker
from googletrans import Translator
from googletrans.constants import LANGUAGES

import datetime
from datetime import datetime as dtime


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stopWatches = {}
        self.bot.help_command.cog = self
        self.passErrors = (commands.CommandNotFound)
        print("Loaded", __name__)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not isinstance(error, self.passErrors):
            try:
                await ctx.send(f"```{str(error)}```")
            except Exception as e:
                print(e, error)


    @commands.command(aliases=['ac'], brief="Autocorrects a set number of messages, default is 5", help="Autocorrects a set number of messages, default is 5")
    async def autocorrect(self, ctx, *limit):
      if not limit:
        limit = 5
      else:
        limit = limit[0]
      await ctx.message.delete()
      async for message in ctx.channel.history(limit=int(limit)):
        if message.id != ctx.message.id and message.author.id == self.bot.user.id:
          newMessage = ""
          for word in message.content.split():
            if not word in self.config['ignoredWords']:
              newMessage += SpellChecker().correction(word)
              newMessage += " "
          if newMessage:
            await message.edit(content=newMessage)


    @commands.command(brief="Stops the autocorrect form correcting a word", help="Stops the autocorrect from correcting a word")
    async def ignoreword(self, ctx, word):
      self.config['ignoredWords'].append(word)
      saveData(self.name, self.config)
      await ctx.send(f"```Autocorrect will no longer correct the word {word}```")


    @commands.command(brief="Autocorrect will no longer ignore a word", help="Autocorrect will no longer ignore a word")
    async def unignoreword(self, ctx, word):
      self.config['ignoredWords'].remove(word)
      saveData(self.name, self.config)
      await ctx.send(f"```Autocorrect will now correct the word {word}```")


    @commands.command(brief="Spams a message", help="Spams a message")
    async def spam(self, ctx, *, message):
    	self.spamming = True
    	while self.spamming:
    		await ctx.send(message)


    @commands.command(brief="Stops spamming a message", help="Stops spamming a message")
    async def stopspam(self, ctx):
    	self.spamming = False


    @commands.command(description="member_or_role can be the name, id, or mention of a role or member", help="Returns the permissions for a role of member in the current server")
    @commands.guild_only()
    async def perms(self, ctx, member_or_role=None):
        def convertPermtoEmoji(member, perm, permissions):
            if getattr(permissions, perm) == True:
                return "✅"
            elif getattr(permissions, perm) == False:
                return "❌"

        if member_or_role == None:
            member_or_role = ctx.author
        else:
            try:
                member_or_role = await Converters.RoleConverter.convert(ctx, member_or_role)
            except commands.RoleNotFound:
                member_or_role = await Converters.MemberConverter.convert(ctx, member_or_role)


        embed = discord.Embed(title=f"Perms for {str(member_or_role)} in {ctx.guild.name}", color=embedColors["Red"])

        if type(member_or_role) == discord.Member:
            permissions = member_or_role.guild_permissions

        elif type(member_or_role) == discord.Role:
            permissions = member_or_role.permissions

        for perm in permissions:
            embed.add_field(name=perm[0].replace('_', ' ').title(), value=convertPermtoEmoji(member_or_role, perm[0], permissions))

        await ctx.reply(embed=embed)


    @commands.command(description="<user> can be the name, id, or mention of a Discord user", help="Returns the profile picture of a Discord user", aliases=['pfp', 'profile'])
    async def avatar(self, ctx, *user : discord.User):
        user = ctx.author if not user else user[0]
        await ctx.reply(user.avatar_url)


    @commands.command(aliases=['purge'], brief="Clears a number of messages", help="Clears a number of messages")
    async def clear(self, ctx, num, *member: discord.User):
    	def is_member(m):
    		return m.author == member

    	def no_check(m):
    		return True

    	if num.lower() == "all":
    		num = None
    	else:
    		num = int(num)

    	if member:
    		member = member[0]
    		check = is_member
    	else:
    		check = no_check

    	if not ctx.guild:
    		messages = await ctx.channel.history(limit=num).flatten()
    		for m in messages:
    			if check(m):
    				try:
    					await m.delete()
    				except:
    					pass
    	else:
    		await ctx.channel.purge(limit=num, check=check)


    @commands.command(help="Starts a stopwatch if there is no active one")
    async def starttimer(self, ctx):
        if self.stopWatches.get(ctx.author.id):
            raise commands.BadArgument("Stop watch already in use")
        await ctx.reply("Starting stopwatch")
        self.stopWatches[ctx.author.id] = dtime.utcnow()


    @commands.command(help="Stops a stopwatch if there is an active one")
    async def stoptimer(self, ctx):
        startTime = self.stopWatches.get(ctx.author.id)
        if not startTime:
            raise commands.BadArgument("No active stopwatches")
        seconds = (dtime.utcnow() - startTime).total_seconds()
        await ctx.reply(f"Ended timer. Timer ran for: {datetime.timedelta(seconds=seconds).strftime('%H:%M:%S %m/%d/%')}")
        del self.stopWatches[ctx.author.id]


    @commands.command(aliases=['alive'], brief="Checks the ping of the bot", help="Checks the ping of the bot")
    async def ping(self, ctx):
      embed = discord.Embed(title="Self-Bot is alive", description=(f"Ping:"), color=embedColors["Red"])
      before = await ctx.send(embed=embed)
      embed = discord.Embed(title="Self-Bot is alive", description=(f"Ping: {(before.created_at - ctx.message.created_at).total_seconds() * 1000}ms"), color=embedColors["Red"])
      await before.edit(embed=embed)


    @commands.command(brief="Returns the definition of a word", help="Returns the definition of a word")
    async def define(self, ctx, word):
        embed = discord.Embed(title=f"Definition of '{word}'", description=None, color=embedColors["Green"])
        meanings = PyDictionary().meaning(word)
        for item in meanings:
            message = ""
            for meaning in meanings[item]:
                message += f"\n{meaning}"
            embed.add_field(name=item, value=message, inline=False)
        await ctx.send(embed=embed)


    @commands.command(brief="Unpins all messages in a channel", help="Unpins all messages in a channel")
    async def unpinall(self, ctx):
        await ctx.send(f"Are you sure you want me too unpin {len(await ctx.channel.pins())} messages? (y/n)")
        def check(m):
            responses = ['y', 'n']
            return ctx.author == m.author and ctx.channel == m.channel and msg.content in responses
        msg = await bot.wait_for('message', timeout=60.0, check=check)
        if msg.content == "y":
            for message in await ctx.channel.pins():
                await message.unpin()
            await ctx.send(f"Unpinned all messages")
        elif msg.content == "n":
            await ctx.send("Cancelled")


    @commands.command(brief="Uses Google Translate to translate a message into English", help="Uses Google Translate to translate a message into English")
    async def translate(self, ctx, *, message):
        embed = discord.Embed(title=f'Translation of "{message}"', color=embedColors["Green"])
        translation = Translator().translate(message, dest='en')
        embed.add_field(name=LANGUAGES[translation.src.lower()].capitalize(), value=message, inline=False)
        embed.add_field(name=LANGUAGES[translation.dest].capitalize(), value=translation.text, inline=False)
        await ctx.send(embed=embed)


    @commands.command(brief="Marks a server as read", help="Marks a server as read", aliases=['markasread', 'mar'])
    async def ack(self, ctx):
        await ctx.guild.ack()


def setup(bot):
    bot.add_cog(Misc(bot))
