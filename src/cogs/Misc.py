import discord
from discord.ext import commands

import src.utils as utils
from src.utils import Color, Converters

from PyDictionary import PyDictionary
PyDictionary = PyDictionary()

from spellchecker import SpellChecker
SpellChecker = SpellChecker()

from googletrans import Translator
from googletrans.constants import LANGUAGES
Translator = Translator()

import datetime
from datetime import datetime as dtime


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stopWatches = {}
        self.bot.help_command.cog = self


    @commands.command(aliases=['ac'], brief="Autocorrects a set number of messages, default is 5", help="Autocorrects a set number of messages, default is 5")
    async def autocorrect(self, ctx):
        if not ctx.message.reference:
            raise commands.BadArgument("You must reply to a message to autocorrect")

        old_message = await self.bot.get_message_reference(ctx.message.reference, ctx.channel)

        if old_message.author != ctx.author:
            raise commands.BadArgument("You can only autocorrect your own messages")

        corrected_message = SpellChecker.correction(old_message.content)
        await old_message.edit(content=corrected_message)


    @commands.command(brief="Stops the autocorrect form correcting a word", help="Stops the autocorrect from correcting a word")
    async def ignoreword(self, ctx, word):
      self.bot.config.ignored_words.append(word)
      self.bot.config.ignored_words = self.bot.config.ignored_words
      embed = discord.Embed(title=f"Autocorrect will now ignore the word {word}", color=Color.red())
      await ctx.reply(embed=embed)


    @commands.command(brief="Autocorrect will no longer ignore a word", help="Autocorrect will no longer ignore a word")
    async def unignoreword(self, ctx, word):
      try:
          self.bot.config.ignored_words.remove(word)
      except ValueError:
          pass
      self.bot.config.ignored_words = self.bot.config.ignored_words
      embed = discord.Embed(title=f"Autocorrect will no longer ingore the word {word}", color=Color.red())
      await ctx.reply(embed=embed)


    @commands.command(brief="Shows all words that are ignored by autocorrect", help="Shows all words that are ignored by autocorrect")
    async def ignoredwords(self, ctx):
        message = "```Words ignored by autocorrect: \n"
        for word in self.bot.config.ignored_words:
            message += word
            message += "\n"
        message += "```"
        await ctx.reply(message)


    @commands.command(brief="Spams a message", help="Spams a message")
    async def spam(self, ctx, *, message):
        embed = discord.Embed(title=f"To stop spamming, use {self.bot.command_prefix(self.bot, ctx)}stopspam")
        await ctx.reply(embed=embed)

    	self.spamming = True
    	while self.spamming:
            await ctx.send(message)
            await asyncio.sleep(1)


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


        embed = discord.Embed(title=f"Perms for {str(member_or_role)} in {ctx.guild.name}", color=Color.red())

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
        self.stopWatches[ctx.author.id] = datetime.utcnow()


    @commands.command(help="Stops a stopwatch if there is an active one")
    async def stoptimer(self, ctx):
        startTime = self.stopWatches.get(ctx.author.id)
        if not startTime:
            raise commands.BadArgument("No active stopwatches")
        seconds = (datetime.utcnow() - startTime).total_seconds()
        await ctx.reply(f"Ended timer. Timer ran for: {datetime.timedelta(seconds=seconds)}")
        del self.stopWatches[ctx.author.id]


    @commands.command(description="For accurate ping readings, this is ratelimited to 1 use every 5 seconds per guild", help="Checks GamerBot's Ping")
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def ping(self, ctx):
        t = await ctx.reply("Pong!")
        await t.edit(content=f'Pong! `{(t.created_at-ctx.message.created_at).total_seconds() * 1000}ms`')


    @commands.command(brief="Returns the definition of a word", help="Returns the definition of a word")
    async def define(self, ctx, word):
        embed = discord.Embed(title=f"Definition of '{word}'", color=Color.green())
        meanings = PyDictionary.meaning(word)
        print("test")
        for item in meanings:
            message = ""
            for meaning in meanings[item]:
                message += f"\n{meaning}"
            embed.add_field(name=item, value=message, inline=False)
        await ctx.reply(embed=embed)


    @commands.command(brief="Unpins all messages in a channel", help="Unpins all messages in a channel")
    async def unpinall(self, ctx):
        await ctx.send(f"Are you sure you want me too unpin {len(await ctx.channel.pins())} messages? (y/n)")
        def check(m):
            responses = ['y', 'n']
            return ctx.author == m.author and ctx.channel == m.channel and msg.content in responses
        msg = await self.bot.wait_for('message', timeout=60.0, check=check)
        if msg.content == "y":
            for message in await ctx.channel.pins():
                await message.unpin()
            await ctx.send(f"Unpinned all messages")
        elif msg.content == "n":
            await ctx.send("Cancelled")


    @commands.command(brief="Uses Google Translate to translate a message into English", help="Uses Google Translate to translate a message into English")
    async def translate(self, ctx, *, message):
        translation = Translator.translate(message, dest='en')
        embed = discord.Embed(color=Color.green())
        embed.add_field(name=LANGUAGES[translation.src.lower()].capitalize(), value=message, inline=False)
        embed.add_field(name=LANGUAGES[translation.dest].capitalize(), value=translation.text, inline=False)
        await ctx.send(embed=embed)


    @commands.command(brief="Marks a server as read", help="Marks a server as read", aliases=['markasread', 'mar'])
    async def ack(self, ctx):
        await ctx.guild.ack()


    @commands.command(brief="Changes the Self-Bot's prefix", help="Changes the Self-Bot's prefix")
    async def changeprefix(self, ctx, prefix):
        self.bot.config.prefix = prefix
        embed = discord.Embed(title=f"Your Self-Bot will now use the prefix {prefix}", description="You can still use .help incase you forget your prefix", color=Color.red())
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
