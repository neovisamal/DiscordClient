import discord
from discord.ext import commands

from src.help import EmbedHelpCommand
from src.utils import Color, Config


class Bot(commands.Bot):
    def __init__(bot):
        super().__init__(command_prefix=bot.determine_prefix, case_insensitive=True, self_bot=True, help_command=EmbedHelpCommand(), allowed_mentions=discord.AllowedMentions.none())

        try:
            bot.config = Config.from_file()
        except (FileNotFoundError):
            bot.config = Config()

        if not bot.config.cogs:
            bot.load_extension("src.cogs.Setup")
        else:
            for cog in bot.config.cogs:
                bot.load_extension(f"src.cogs.{cog}")
            bot.load_extension("src.cogs.ErrorHandler")


    def run(self, *args, **kwargs):
        try:
            super().run(*args, **kwargs)
        except:
            return False


    @staticmethod
    def determine_prefix(bot, ctx):
        return bot.config.prefix


    @staticmethod
    async def get_message(message: discord.Message):
        async for m in message.channel.history(limit=25):
            if message.id == m.id:
                return m


    async def on_ready(bot):
        print("Logged into", bot.user)
        for cog in bot.cogs:
            print("Loaded", cog)
        bot.add_command(bot.setup)
        bot.config.TOKEN = bot.http.token


    @commands.command()
    async def setup(ctx):
        bot = ctx.bot

        cogs = {
         "📝" : "Logger",
         "⚙️" : "Misc",
        }

        embed = discord.Embed(title="Setup Menu", description="Select what features you would like to enable", color=Color.red())
        embed.add_field(name="React 📝 to enable Logger", value="\u200b", inline=False)
        embed.add_field(name="React ⚙️ to enable commands", value="\u200b", inline=False)
        embed.add_field(name="React ✅ to confirm", value="\u200b", inline=False)

        message = await ctx.reply(embed=embed)
        for key, value in cogs.items():
            await message.add_reaction(key)

        def check(reaction, user):
            return user == ctx.author and reaction.message == message and str(reaction) == "✅"

        reaction, user = await bot.wait_for('reaction_add', timeout=120.0, check=check)

        selected_cogs = [str(reaction) for reaction in reaction.message.reactions]
        selected_cogs.remove("✅")
        selected_cogs = [cogs[cog] for cog in selected_cogs]

        bot.config.cogs = selected_cogs

        embed = discord.Embed(title="Your Self-Bot is setup! You can always use the setup command to edit which features you would like enabled")
        await ctx.reply(embed=embed)


        for cog in selected_cogs:
            bot.load_extension(f"src.cogs.{cog}")

        bot.load_extension("src.cogs.ErrorHandler")
        bot.unload_extension("src.cogs.Setup")
