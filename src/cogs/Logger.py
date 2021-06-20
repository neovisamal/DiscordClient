import src.utils as utils

import discord
from discord.ext import commands

import asyncio


class LoggedMessage:
    def __init__(self, message: discord.Message, type, color: discord.Color):
        if message.guild:
            icon_url = message.guild.icon_url
            guild = message.guild.name + ": "
        else:
            guild = ""

            try:
                icon_url = message.channel.recipient.avatar_url
            except AttributeError:
                icon_url = message.channel.icon_url

        content = str(message.content)

        embed = discord.Embed(title=f"{type} in {guild}{message.channel}", description=f"Message by {str(message.author)}", color=color)

        embed.add_field(name="Message:", value=content[0:1000], inline=False)

        if message.attachments:
            attachments = ""
            for attachment in message.attachments:
                attachments += attachment.url
                attachments += "\n"
            embed.add_field(name="Attachments", value=attachments, inline=False)

        embed.set_thumbnail(url=message.author.avatar_url)
        embed.set_footer(text=f"Message sent at {utils.UTCtoPST(message.created_at)} PST", icon_url=icon_url)

        self.embed = embed


    def __str__(self):
        return self.embed


def DeletedMessage(message):
    return LoggedMessage(message, "Message deleted", "Red")


def EditedMessage(before, after):
    embed = LoggedMessage(before, "Message edited", "Orange")

    content = checkIfNone(after.content, "None")

    embed.add_field(name="New Message:", value=content[0:2000], inline=False)

    try:
        embed.add_field(name="Edited at:", value=UTCtoPST(after.edited_at), inline=False)
    except:
        pass

    return embed


def ReactionMessage(type, reaction, user, message):
    typeColor = {
    "added": 'Yellow',
    "removed": "Purple"
    }

    embed = LoggedMessage(message, f"Reaction {type}", typeColor[type])
    embed.add_field(name="User", value=str(user), inline=False)
    embed.add_field(name="Reaction", value=reaction.emoji, inline=False)
    return embed




class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.load_config()
        if not self.config.get("ignoredUsers")
        self.messageLog = {}


    def checkIfLog(self, message):
        if (not message.author.bot and not message.author.id in self.config['ignoredUsers']) and (not message.guild or message.guild.id in self.config['loggingGuilds']):
            return True
        else:
            return False


    @commands.Cog.listener()
    async def on_ready(self):
        self.alt = self.bot.get_user(self.config['altID'])


    @commands.Cog.listener()
    async def on_message(self, message):
        if self.checkIfLog(message):
            message = await self.bot.get_message(message)
            if message:
                self.messageLog[message.id] = message


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if self.messageLog.get(message.id):
            message = self.messageLog.get(message.id)
            embed = DeletedMessage(message)
            await self.alt.send(embed="e")


    #@commands.Cog.listener()
    async def on_message_edit(self, before, after):
        before = self.messageLog.get(before.id)
        if before:
            async for message in after.channel.history(limit=50):
                if message.id == after.id:
                    after = message
                    break
            self.messageLog[after.id] = after
            embed = EditedMessage(before, after)
            await self.alt.send(embed=embed)


    #@commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        message = self.messageLog.get(reaction.message.id)
        if message:
            embed = ReactionMessage("added", reaction, user, message)
            await self.alt.send(embed=embed)


    #@commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        message = self.messageLog.get(reaction.message.id)
        if message:
            embed = ReactionMessage("removed", reaction, user, message)
            await self.alt.send(embed=embed)


    @commands.command(brief="Logs deleted and edited messages in a server", help="Logs deleted and edited messages in a server")
    @commands.guild_only()
    async def logserver(self, ctx):
        if ctx.guild.id in self.config['loggingGuilds']:
            return await ctx.send(f"```Already logging {ctx.guild.name}```")
        self.config['loggingGuilds'].append(ctx.guild.id)
        saveData(self.name, self.config)
        await ctx.send(f"```You are now logging {ctx.guild.name}```")


    @commands.command(brief="Stops logging deleted and edited messages in a server", help="Stops logging deleted and edited messages in a server")
    @commands.guild_only()
    async def unlogserver(self, ctx):
        if not ctx.guild.id in self.config['loggingGuilds']:
            return await ctx.send(f"```Already not logging {ctx.guild.name}```")
        self.config['loggingGuilds'].remove(ctx.guild.id)
        saveData(self.name, self.config)
        await ctx.send(f"```You are no longer logging {ctx.guild.name}```")


    @commands.command(brief="Displays a list of all servers being logged", help="Displays a list of all servers being logged")
    async def loggedservers(self, ctx):
        message = ""
        for id in self.config['loggingGuilds']:
            guild = self.bot.get_guild(id)
            if guild:
                message += f"\n{guild.name}"
        await ctx.send(f"```Servers currently being logged: {message}```")


    @commands.command(brief="Stops logging a users deleted and edited messages", help="Stops logging a users deleted and edited messages")
    async def ignore(self, ctx, user : discord.User):
        if user.id in self.config['ignoredUsers']:
            return await ctx.send(f"```Already ignoring {str(user)}```")
        self.config['ignoredUsers'].append(user.id)
        saveData(self.name, self.config)
        await ctx.send(f"```You are now ignoring {str(user)}```")


    @commands.command(brief="Starts logging a users deleted and edited messages", help="Starts logging a users deleted and edited messages")
    async def unignore(self, ctx, user : discord.User):
        if not user.id in self.config['ignoredUsers']:
            return await ctx.send(f"```Already not ignoring {str(user)}```")
        self.config['ignoredUsers'].remove(user.id)
        saveData(self.name, self.config)
        await ctx.send(f"```You are no longer ignoring {str(user)}```")


    @commands.command(brief="Displays a list of all users being ignored", help="Displays a list of all users being ignored")
    async def ignoredusers(self, ctx):
        message = ""
        for id in self.config['ignoredUsers']:
            user = self.bot.get_user(id)
            message += f"\n{str(user)}"
        await ctx.send(f"```Users currently being ignored: {message}```")


def setup(bot):
    bot.add_cog(Logger(bot))
