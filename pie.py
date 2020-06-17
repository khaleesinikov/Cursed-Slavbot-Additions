import discord # imports main discord module
from discord.ext import commands # imports the bot specific parts
from datetime import datetime

print(discord.__version__)

description = '''An example bot to showcase the
discord.ext.commands extension module. There are a number of utility commands being
showcased here.'''  # triple ' means multi line string

bot = commands.Bot(command_prefix='s!', description=description)  # initialises bot object with a prefix

statuses = {
    "online": "🟢 ONLINE",
    "idle": "🟠 AWAY",
    "offline": "⚪ OFFLINE",
    "do_not_disturb": "🔴 DO NOT DISTURB",
    "dnd": "🔴 DO NOT DISTURB"
}


@bot.event
async def on_command_error(context, exception):
    print("oh no an error", exception)
    if type(exception) == discord.ext.commands.errors.CommandNotFound:
        return


@bot.event  # this is a "decorator" (like from java) it means "this function is overriding one of the ones in bot.event"
async def on_ready():  # this function runs when the bot has logged in
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()  # this says "this function is a command, when you do the prefix + the function name run this function
async def add(ctx, left: int, right: int):  # so saying s!add 1 2 would make it say 3
    """Adds two numbers together."""
    await ctx.send(left + right)  # ctx is a "context" object that just stores a load of information about the message


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


@bot.command()
async def who(ctx):
    message = "**Channel**: " + ctx.channel.name\
              + "\n**Author**: " + ctx.author.name\
              + "\n**Author Join Date**: " + ctx.author.joined_at.strftime("%d/%m/%Y")
    await ctx.send(message)


@bot.command()
async def whom(ctx):
    if not ctx.message.mentions:
        member = ctx.author
    else:
        member = ctx.message.mentions[0]
    embed = discord.Embed(title="Who this?", color=member.roles[-2].colour)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Name", value=member.name, inline=True)
    embed.add_field(name="Status", value=statuses[str(member.status)], inline=True)
    if not member.bot:
        people = [member.name for member in sorted(ctx.guild.members, key=lambda z: z.joined_at) if not member.bot]
        join_order = ""
        for x in range(people.index(member.name) - 2, people.index(member.name) + 3):
            if x < 0 or x > len(people) - 1:
                continue
            if people[x] == member.name:
                join_order += "**{}**".format(member.name)
                if not x == len(people) - 1 and not x == people.index(member.name) + 2:
                    join_order += " > "
            else:
                join_order += people[x]
                if not x == len(people) - 1 and not x == people.index(member.name) + 2:
                    join_order += " > "
        embed.add_field(name="Join Rank", value="#" + str(people.index(member.name)+1), inline=True)
        embed.add_field(name="Join Order", value=join_order, inline=False)
    embed.add_field(name="Roles", value=', '.join(reversed(['`{}`'.format(role.name) for role in member.roles[1:-1]])),
                    inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)  # replace the word token with slavbots token
