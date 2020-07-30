import random
import string
from datetime import datetime
import discord
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
    text += "\nRemaining guesses: " + str(7 - incorrect_guesses[server_id]) + "\nAlready guessed: " + str(letters)[1:-1]
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
        self.database = bot.database
        self.cursor = self.database.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS hangman (" +
                            "user TEXT UNIQUE," +
                            "wins INTEGER," +
                            "losses INTEGER," +
                            "gains INTEGER)")
        self.cursor.execute("UPDATE players SET in_game='no'")
        self.database.commit()

    @commands.group(invoke_without_command=True, aliases=["hm"])
    async def hangman(self, ctx):
        if ctx.guild.id in gamers:
            await ctx.send("There's already a game going on this server, finish it first!")
            return
        self.cursor.execute("SELECT * FROM players WHERE user=?", (str(ctx.author.id),))
        entry = self.cursor.fetchone()
        if entry is None:
            today_date = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("INSERT INTO players (user,balance,net,in_game,last_daily) VALUES (?, 250, 0, 'no', ?)",
                                (str(ctx.author.id), today_date))
            self.cursor.execute("INSERT INTO blackjack (user,games,gains) VALUES (?, 0, 0)",
                                (str(ctx.author.id),))
            self.database.commit()
            await ctx.send("You have been awarded 250 SlavStocks(tm) as a starting balance.")
        elif entry[3] == "yes":
            await ctx.send("You're already in a game, let's not get ahead of ourselves.")
            return
        self.cursor.execute("UPDATE players SET in_game='yes' WHERE user=?", (str(ctx.author.id),))
        self.database.commit()
        self.cursor.execute("SELECT * FROM hangman WHERE user=?", (str(ctx.author.id),))
        entry = self.cursor.fetchone()
        if entry is None:
            self.cursor.execute("INSERT INTO hangman (user,wins,losses,gains) VALUES (?, 0, 0, 0)",
                                (str(ctx.author.id),))
            self.database.commit()
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
        self.cursor.execute("SELECT * FROM players WHERE user=?", (str(ctx.author.id),))
        entry = self.cursor.fetchone()
        if entry is None:
            today_date = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("INSERT INTO players (user,balance,net,in_game,last_daily) VALUES (?, 250, 0, 'no', ?)",
                                (str(ctx.author.id), today_date))
            self.cursor.execute("INSERT INTO blackjack (user,games,gains) VALUES (?, 0, 0)",
                                (str(ctx.author.id),))
            self.database.commit()
            await ctx.send("You have been awarded 250 SlavStocks(tm) as a starting balance.")
        elif entry[3] == "yes":
            await ctx.send("You're already in a game, let's not get ahead of ourselves.")
            return
        self.cursor.execute("UPDATE players SET in_game='yes' WHERE user=?", (str(ctx.author.id),))
        self.database.commit()
        self.cursor.execute("SELECT * FROM hangman WHERE user=?", (str(ctx.author.id),))
        entry = self.cursor.fetchone()
        if entry is None:
            self.cursor.execute("INSERT INTO hangman (user,wins,losses,gains) VALUES (?, 0, 0, 0)",
                                (str(ctx.author.id),))
            self.database.commit()
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
                if victory_check(server):
                    winnings = 70 - (incorrect_guesses[server] * 10)
                    await message.channel.send(f"All gamers have received 10 SlavStocks(tm) for each remaining guess, "
                                               f"for a total of {winnings} SlavStocks(tm).")
                for gamer in gamers[server]:
                    self.cursor.execute("UPDATE players SET in_game='no' WHERE user=?", (str(gamer),))
                    self.database.commit()
                    if incorrect_guesses[server] == 7:
                        self.cursor.execute("SELECT * FROM hangman WHERE user=?", (str(gamer),))
                        temp = self.cursor.fetchone()
                        self.cursor.execute("UPDATE hangman SET losses=? WHERE user=?", (temp[2] + 1, str(gamer)))
                        self.database.commit()
                    elif victory_check(server):
                        winnings = 70 - (incorrect_guesses[server] * 10)
                        self.cursor.execute("SELECT * FROM hangman WHERE user=?", (str(gamer),))
                        temp = self.cursor.fetchone()
                        self.cursor.execute("UPDATE hangman SET wins=?, gains=? WHERE user=?",
                                            (temp[1] + 1, temp[3] + winnings, str(gamer)))
                        self.cursor.execute("SELECT * FROM players WHERE user=?", (str(gamer),))
                        temp = self.cursor.fetchone()
                        self.cursor.execute("UPDATE players SET balance=?, net=? WHERE user=?",
                                            (temp[1] + winnings, temp[2] + winnings, str(gamer)))
                        self.database.commit()
                del guesses[server]
                del current_words[server]
                del gamers[server]
                del incorrect_guesses[server]

    @hangman.command(name='stats')
    async def hang_stats(self, ctx):
        if not ctx.message.mentions:
            member = ctx.author
        else:
            member = ctx.message.mentions[0]
        embed = discord.Embed(title="Hangman stats for " + member.name, color=discord.Color.blurple())
        self.cursor.execute("SELECT * FROM hangman WHERE user=?", (str(member.id),))
        temp = self.cursor.fetchone()
        if temp is None:
            await ctx.send("404: stats not found")
            return
        embed.add_field(name='Wins', value=str(temp[1]))
        embed.add_field(name='Losses', value=str(temp[2]))
        embed.add_field(name='Earnings', value=str(temp[3]))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Hangman(bot))
