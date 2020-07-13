import discord
from discord.ext import commands


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def poll(self, ctx, *question):
        embed = discord.Embed(title=' '.join(question), description="Created by: " + ctx.author.name)
        embed.add_field(name='👍', value="Yes")
        embed.add_field(name='👎', value="No")
        message = await ctx.channel.send(embed=embed)
        await message.add_reaction('👍')
        await message.add_reaction('👎')
        embed.set_footer(text='Poll ID: {}'.format(message.id))
        await message.edit(embed=embed)

    @poll.command(name="-o")
    async def options(self, ctx, *message):
        reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
        message = ' '.join(message)
        question = message.split(";")[0]
        options = message.split(";")[1].split(",")
        if len(options) <= 1:
            await ctx.send("Fun fact, if you only have one option that's not a poll.")
            return
        if len(options) > 10:
            await ctx.send("The option limit is 10, calm down.")
            return
        embed = discord.Embed(title=question, description="Created by: " + ctx.author.name)
        for x, option in enumerate(options):
            embed.add_field(name=reactions[x], value=option)
        message = await ctx.channel.send(embed=embed)
        embed.set_footer(text='Poll ID: {}'.format(message.id))
        await message.edit(embed=embed)
        for reaction in reactions[:len(options)]:
            await message.add_reaction(reaction)

    @commands.command()
    async def tally(self, ctx, poll_id):
        message = await ctx.channel.fetch_message(poll_id)
        if not message.embeds:
            await ctx.send("That message is not a valid poll!")
            return
        if message.author.id != self.bot.user.id:
            await ctx.send("That message is not a valid poll!")
            return
        if not message.embeds[0].footer.text.startswith("Poll ID:"):
            await ctx.send("That message is not a valid poll!")
            return
        options = message.embeds[0].fields
        embed = discord.Embed(title=message.embeds[0].title, description=message.embeds[0].description)
        tally = {}
        option_names = {}
        for option in options:
            tally[option.name] = 0
            option_names[option.name] = option.value
        for reaction in message.reactions:
            if reaction.emoji in tally.keys():
                tally[reaction.emoji] = len(await reaction.users().flatten())-1
                embed.add_field(name=reaction.emoji + " " + option_names[reaction.emoji],
                                value=str(tally[reaction.emoji]))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Poll(bot))
