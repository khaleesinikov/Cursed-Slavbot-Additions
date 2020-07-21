import random
import string

from discord.ext import commands

valid_chars = list(string.ascii_lowercase)

gallows = ['''
    +---+
        |
        |
        |
        |
        |
  ========''', '''
    +---+
    |   |
        |
        |
        |
        |
  ========''', '''
    +---+
    |   |
    o   |
        |
        |
        |
  ========''', '''
    +---+
    |   |
    o   |
    |   |
        |
        |
  ========''', '''
    +---+
    |   |
    o   |
   /|   |
        |
        |
  ========''', '''
    +---+
    |   |
    o   |
   /|\\  |
        |
        |
  ========''', '''
    +---+
    |   |
    o   |
   /|\\  |
   /    |
        |
  ========''', '''
    +---+
    |   |
    o   |
   /|\\  |
   / \\  |
        |
  ========''']

gamers = {}

guesses = {}

incorrect_guesses = {}

current_words = {}


def make_display(server_id):
    word = current_words[server_id]
    letters = guesses[server_id]
    text = "```python\n"
    text += gallows[incorrect_guesses[server_id]] + "\n"
    if word in letters:
        for letter in word:
            text += letter + " "
    else:
        for letter in word:
            if letter in letters:
                text += letter + " "
            else:
                text += "_ "
    text += "\nRemaining guesses: " + str(7 - incorrect_guesses[server_id]) + "\u0009Already guessed: " + str(letters)
    if incorrect_guesses[server_id] == 7 and not victory_check(server_id):
        text += "\nYou lost :(\nThe word was: '" + current_words[server_id] + "'.```"
    elif victory_check(server_id):
        text += "\nYou won :D\nSlavbot congratulates you.```"
    else:
        text += "\nUse 's!hm join' to participate.\nPrefix word guesses with '>'.```"
    return text


def validity_check(guess):
    for letter in guess:
        if letter not in valid_chars:
            return False
    return True


def victory_check(server_id):
    word = current_words[server_id]
    letters = guesses[server_id]
    if word in letters:
        return True
    for letter in word:
        if letter not in letters:
            return False
    return True


class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=["hm"])
    async def hangman(self, ctx):
        if ctx.guild.id in gamers:
            await ctx.send("There's already a game going on this server, finish it first!")
            return
        gamers[ctx.guild.id] = [ctx.author.id]
        guesses[ctx.guild.id] = []
        incorrect_guesses[ctx.guild.id] = 0
        f = open("difficult.txt", "r")
        raw = f.read()
        words = raw.split(",")
        word = random.choice(words)
        current_words[ctx.guild.id] = word
        await ctx.send("Starting hangman game...")
        await ctx.send(make_display(ctx.guild.id))

    @hangman.command(name='join')
    async def join_hangman(self, ctx):
        if ctx.guild.id not in gamers:
            await ctx.send("There's no game for you to join! Try starting one.")
            return
        gamers[ctx.guild.id].append(ctx.author.id)
        await ctx.send(ctx.author.name + " successfully joined the hangman game!")

    @commands.Cog.listener()
    async def on_message(self, message):
        server = message.guild.id
        if server not in gamers:
            return
        if message.author.id in gamers[server]:
            guess = message.content.lower()
            if len(guess) == 1 and validity_check(guess):
                if guess in guesses[server]:
                    await message.channel.send(guess + " has already been guessed.")
                    return
                else:
                    guesses[server].append(guess)
                    if guess not in current_words[server]:
                        incorrect_guesses[server] += 1
            elif guess.startswith('>'):
                guess = guess[1:]
                if guess in guesses[server]:
                    await message.channel.send("'" + guess + "' has already been tried.")
                    return
                elif not validity_check(guess):
                    await message.channel.send("'" + guess + "' is not a valid guess.")
                    return
                else:
                    guesses[server].append(guess)
                    if guess != current_words[server]:
                        incorrect_guesses[server] += 1
            else:
                return
            await message.channel.send(make_display(server))
            if incorrect_guesses[server] == 7 or victory_check(server):
                await message.channel.send("This game of hangman has finished!")
                del guesses[server]
                del current_words[server]
                del gamers[server]
                del incorrect_guesses[server]


def setup(bot):
    bot.add_cog(Hangman(bot))
