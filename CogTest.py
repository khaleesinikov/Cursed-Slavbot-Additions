from discord.ext import commands


class CogTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def latency(self, ctx):
        await ctx.send(str(round(self.bot.latency, 6)) + " seconds")


def setup(bot):
    bot.add_cog(CogTest(bot))
