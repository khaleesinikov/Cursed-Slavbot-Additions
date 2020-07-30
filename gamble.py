from datetime import datetime
from math import ceil
import discord
import pydealer
from discord.ext import commands


def unparser(money):
    money = str(money).lower()
    if money.endswith("m"):
        currency = money[:-1] + "000000"
    elif money.endswith("k"):
        currency = money[:-1] + "000"
    else:
        currency = money
    try:
        currency = int(currency)
    except ValueError:
        return "lol bad"
    return int(currency)


suit_map = {'Diamonds': '\u2662',
            'Clubs': '\u2667',
            'Hearts': '\u2661',
            'Spades': '\u2664'}

dealt_hands = {}

player_decks = {}

player_bets = {}


def calculate_value(hand):
    num_aces = 0
    total_value = 0
    for card in hand:
        if pydealer.const.DEFAULT_RANKS['values'][card.value] == 13:
            num_aces += 1
            total_value += 11
        elif pydealer.const.DEFAULT_RANKS['values'][card.value] >= 10:
            total_value += 10
        else:
            total_value += int(card.value)

    while num_aces > 0 and total_value > 21:
        total_value -= 10
        num_aces -= 1
    return total_value


def make_display(user, hand, bet, val):
    text = "```python\n"
    text += "Player: " + user + "\u0009"
    text += "Bet amount: " + str(bet) + "\u0009"
    text += "Hand value: " + str(val) + "\n"
    for card in hand:
        suit = suit_map[card.suit]
        if pydealer.const.DEFAULT_RANKS['values'][card.value] >= 10:
            rank = card.value[0]
        else:
            rank = card.value
        text += '| {0:2.2} {1} | '.format(rank, suit)
    text += "\n```"
    return text


class Gamble(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database
        self.cursor = self.database.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS players (" +
                            "user TEXT UNIQUE," +
                            "balance INTEGER," +
                            "net INTEGER," +
                            "in_game TEXT," +
                            "last_daily TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS blackjack (" +
                            "user TEXT UNIQUE," +
                            "games INTEGER," +
                            "gains INTEGER)")
        self.cursor.execute("UPDATE players SET in_game='no'")
        self.database.commit()

    @commands.group(invoke_without_command=True, aliases=["bj"])
    async def blackjack(self, ctx):
        await ctx.send("```Welcome to slavbot's bootleg blackjack!\n" +
                       "To create an account and claim your SlavStocks(tm) use 'claim'.\n" +
                       "To start a game, use 'play' {your bet}.\n" +
                       "To view your stats, use 'stats'.\n" +
                       "To view your rank on this server use 'rank'.\n" +
                       "To claim your 50 daily SlavStocks(tm) use 'daily'.\n" +
                       "To check the rules of the game, use 'rules'.```")

    @blackjack.command(name="claim")
    async def claim(self, ctx):
        self.cursor.execute("SELECT * FROM players WHERE user=?", (str(ctx.author.id),))
        entry = self.cursor.fetchone()
        if entry is None:
            today_date = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("INSERT INTO players (user,balance,net,in_game,last_daily) VALUES (?, 250, 0, 'no', ?)",
                                (str(ctx.author.id), today_date))
            self.cursor.execute("INSERT INTO blackjack (user,games,gains) VALUES (?, 0, 0)",
                                (str(ctx.author.id),))
            self.database.commit()
            await ctx.send("You have been awarded 250 SlavStocks(tm), don't spend them all at once!")
        else:
            await ctx.send("You've already claimed your SlavStocks(tm) smh")

    @blackjack.command(name="rules")
    async def rules(self, ctx):
        rules = "```The aim of the game is to hit 21, or get as close to it as possible, without going over.\nYou're " \
                "dealt a starting hand of 2, and can either 'stand' to finish or 'hit' to get another card.\nYou " \
                "double your bet if you hit 21, 1.25x your bet for 20, and 1.05x for 19 (always rounded up).\nIf you " \
                "finish at 16, 17, or 18 then you leave with your original bet amount. Leave any lower and you lose " \
                "it.\nIf you get above 21, you also lose.\nFace cards are worth 10, number cards are worth their " \
                "number, aces are 1 or 11.\nThe game is played with a standard 52 card deck.``` "
        await ctx.send(rules)

    @blackjack.command(name="play")
    async def start_game(self, ctx, amount):
        self.cursor.execute("SELECT * FROM players WHERE user=?", (str(ctx.author.id),))
        entry = self.cursor.fetchone()
        if entry is None:
            await ctx.send("You don't exist yet, try claiming your SlavStocks(tm) to begin doing so.")
            return
        if entry[3] == "yes":
            await ctx.send("You're already in a game, let's not get ahead of ourselves.")
            return
        if amount == "all":
            bet = entry[1]
        elif amount.isdigit():
            bet = int(amount)
        else:
            bet = unparser(amount)
            if bet == "lol bad":
                await ctx.send("That's a bad number of SlavStocks(tm), try again.")
                return
        if bet > entry[1]:
            await ctx.send("You can't bet more than you have. You have {}.".format(str(entry[1])))
            return
        elif bet <= 0:
            await ctx.send("Nice try.")
            return
        self.cursor.execute("UPDATE players SET in_game='yes' WHERE user=?", (str(ctx.author.id),))
        self.database.commit()
        deck = pydealer.Deck()
        deck.shuffle()
        hand = deck.deal(2)
        hand.sort()
        value = calculate_value(hand)
        await ctx.send(make_display(ctx.author.name, hand, bet, value))
        if value == 21:
            await ctx.send(
                f"You hit 21! You have won {bet * 2} SlavStocks(tm), and now have {entry[1] + bet} SlavStocks(tm).")
            self.cursor.execute("UPDATE players SET in_game='no', balance=?, net=? WHERE user=?",
                                (entry[1] + bet, entry[2] + bet, str(ctx.author.id)))
            self.cursor.execute("SELECT * FROM blackjack WHERE user=?", (str(ctx.author.id),))
            temp = self.cursor.fetchone()
            self.cursor.execute("UPDATE blackjack SET games=?, gains=? WHERE user=?",
                                (temp[1] + 1, temp[2] + bet, str(ctx.author.id)))
            self.database.commit()
        else:
            await ctx.send(f"Your score is {value}. You may now stand or hit.")
            dealt_hands[ctx.author.id] = hand
            player_decks[ctx.author.id] = deck
            player_bets[ctx.author.id] = bet

    @blackjack.command(name='hit')
    async def hit(self, ctx):
        if ctx.author.id not in dealt_hands.keys():
            await ctx.send("You don't seem to be in a game right now.")
            return
        hand = dealt_hands[ctx.author.id]
        deck = player_decks[ctx.author.id]
        bet = player_bets[ctx.author.id]
        hand += deck.deal(1)
        hand.sort()
        value = calculate_value(hand)
        await ctx.send(make_display(ctx.author.name, hand, bet, value))
        self.cursor.execute("SELECT * FROM players WHERE user=?", (str(ctx.author.id),))
        entry = self.cursor.fetchone()
        if value == 21:
            await ctx.send(
                f"You hit 21! You have won {bet * 2} SlavStocks(tm), and now have {entry[1] + bet} SlavStocks(tm).")
            self.cursor.execute("UPDATE players SET in_game='no', balance=?, net=? WHERE user=?",
                                (entry[1] + bet, entry[2] + bet, str(ctx.author.id)))
            self.cursor.execute("SELECT * FROM blackjack WHERE user=?", (str(ctx.author.id),))
            temp = self.cursor.fetchone()
            self.cursor.execute("UPDATE blackjack SET games=?, gains=? WHERE user=?",
                                (temp[1] + 1, temp[2] + bet, str(ctx.author.id)))
            self.database.commit()
            del player_bets[ctx.author.id]
            del player_decks[ctx.author.id]
            del dealt_hands[ctx.author.id]
            return
        elif value > 21:
            await ctx.send(f"Uh oh you got above 21 and lost {bet} SlavStocks(tm) :( You now have {entry[1] - bet} "
                           f"SlavStocks(tm).")
            self.cursor.execute("UPDATE players SET in_game='no', balance=?, net=? WHERE user=?",
                                (entry[1] - bet, entry[2] - bet, str(ctx.author.id)))
            self.cursor.execute("SELECT * FROM blackjack WHERE user=?", (str(ctx.author.id),))
            temp = self.cursor.fetchone()
            self.cursor.execute("UPDATE blackjack SET games=?, gains=? WHERE user=?",
                                (temp[1] + 1, temp[2] - bet, str(ctx.author.id)))
            self.database.commit()
            del player_bets[ctx.author.id]
            del player_decks[ctx.author.id]
            del dealt_hands[ctx.author.id]
            return
        else:
            await ctx.send(f"Your score is {value}. You may now stand or hit.")
            dealt_hands[ctx.author.id] = hand
            player_decks[ctx.author.id] = deck

    @blackjack.command(name='stand')
    async def stand(self, ctx):
        if ctx.author.id not in dealt_hands.keys():
            await ctx.send("You don't seem to be in a game right now.")
            return
        hand = dealt_hands[ctx.author.id]
        value = calculate_value(hand)
        bet = player_bets[ctx.author.id]
        self.cursor.execute("SELECT * FROM players WHERE user=?", (str(ctx.author.id),))
        entry = self.cursor.fetchone()
        if value == 20:
            winnings = ceil(bet * 0.25)
            await ctx.send(
                f"You finished with a score of 20. You won {bet + winnings} SlavStocks(tm) and now have "
                f"{entry[1] + winnings} SlavStocks(tm).")
        elif value == 19:
            winnings = ceil(bet * 0.05)
            await ctx.send(
                f"You finished with a score of 19. You won {bet + winnings} SlavStocks(tm) and now have "
                f"{entry[1] + winnings} SlavStocks(tm).")
        elif value > 15:
            winnings = 0
            await ctx.send(
                f"You finished with a score of {value}. You got your {bet} SlavStocks(tm) back and now have "
                f"{entry[1]} SlavStocks(tm).")
        else:
            winnings = 0 - bet
            await ctx.send(
                f"You finished with a score of {value}. You lost all {bet} SlavStocks(tm) :( You now have "
                f"{entry[1] - bet} SlavStocks(tm).")
        self.cursor.execute("UPDATE players SET in_game='no', balance=?, net=? WHERE user=?",
                            (entry[1] + winnings, entry[2] + winnings, str(ctx.author.id)))
        self.cursor.execute("SELECT * FROM blackjack WHERE user=?", (str(ctx.author.id),))
        temp = self.cursor.fetchone()
        self.cursor.execute("UPDATE blackjack SET games=?, gains=? WHERE user=?",
                            (temp[1] + 1, temp[2] + winnings, str(ctx.author.id)))
        self.database.commit()
        del player_bets[ctx.author.id]
        del player_decks[ctx.author.id]
        del dealt_hands[ctx.author.id]

    @blackjack.command(name='stats')
    async def statistics(self, ctx):
        if not ctx.message.mentions:
            member = ctx.author
        else:
            member = ctx.message.mentions[0]
        embed = discord.Embed(title="Blackjack stats for " + member.name, color=discord.Color.blurple())
        self.cursor.execute("SELECT * FROM blackjack WHERE user=?", (str(member.id),))
        temp = self.cursor.fetchone()
        if temp is None:
            await ctx.send("404: stats not found")
            return
        embed.add_field(name='Games Played', value=str(temp[1]))
        embed.add_field(name='Net Earnings', value=str(temp[2]))
        self.cursor.execute("SELECT * FROM players WHERE user=?", (str(member.id),))
        temp = self.cursor.fetchone()
        embed.add_field(name='Current SlavStocks(tm)', value=str(temp[1]))
        await ctx.send(embed=embed)

    @blackjack.command(name='daily')
    async def daily(self, ctx):
        today_date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("SELECT * FROM players WHERE user=?", (str(ctx.author.id),))
        temp = self.cursor.fetchone()
        if temp is None:
            await ctx.send("You don't exist yet, try claiming your SlavStocks(tm) to begin doing so.")
            return
        if temp[4] == today_date:
            await ctx.send("You've already claimed today's SlavStocks(tm) smh")
            return
        if temp[3] == 'yes':
            await ctx.send("Finish your game first smh")
            return
        self.cursor.execute("UPDATE players SET balance=?, last_daily=? WHERE user=?",
                            (temp[1] + 50, today_date, ctx.author.id))
        await ctx.send("You have been granted 50 SlavStocks(tm), don't spend them all at once!")

    @blackjack.command(name='rank')
    async def rank(self, ctx):
        embed = discord.Embed(title="Blackjack gains for " + ctx.guild.name, color=discord.Color.blurple())
        self.cursor.execute("SELECT * FROM players ORDER BY net DESC")
        temp = self.cursor.fetchall()
        count = 1
        for x in temp:
            user = ctx.guild.get_member(int(x[0]))
            if user is None:
                continue
            embed.add_field(name=str(count) + '. ' + user.name, value=str(x[2]), inline=False)
            count += 1
            if count == 6:
                break
        embed.add_field(name='\u200B', value='\u200B', inline=False)
        embed.add_field(name='Total players', value=str(len(temp)))
        await ctx.send(embed=embed)

    @commands.command(name='balance')
    async def balance(self, ctx):
        self.cursor.execute("SELECT * FROM players WHERE user=?", (str(ctx.author.id),))
        temp = self.cursor.fetchone()
        if temp is None:
            await ctx.send("404: balance not found")
            return
        await ctx.send(f"You have {temp[1]} SlavStocks(tm) available.")

    @commands.Cog.listener()
    async def on_message(self, message):
        gamer = message.author.id
        if gamer not in dealt_hands:
            return
        if message.content.lower() == "hit":
            hand = dealt_hands[gamer]
            deck = player_decks[gamer]
            bet = player_bets[gamer]
            hand += deck.deal(1)
            hand.sort()
            value = calculate_value(hand)
            await message.channel.send(make_display(message.author.name, hand, bet, value))
            self.cursor.execute("SELECT * FROM players WHERE user=?", (str(gamer),))
            entry = self.cursor.fetchone()
            if value == 21:
                await message.channel.send(
                    f"You hit 21! You have won {bet * 2} SlavStocks(tm), and now have {entry[1] + bet} SlavStocks(tm).")
                self.cursor.execute("UPDATE players SET in_game='no', balance=?, net=? WHERE user=?",
                                    (entry[1] + bet, entry[2] + bet, str(gamer)))
                self.cursor.execute("SELECT * FROM blackjack WHERE user=?", (str(gamer),))
                temp = self.cursor.fetchone()
                self.cursor.execute("UPDATE blackjack SET games=?, gains=? WHERE user=?",
                                    (temp[1] + 1, temp[2] + bet, str(gamer)))
                self.database.commit()
                del player_bets[gamer]
                del player_decks[gamer]
                del dealt_hands[gamer]
                return
            elif value > 21:
                await message.channel.send(
                    f"Uh oh you got above 21 and lost {bet} SlavStocks(tm) :( You now have {entry[1] - bet} "
                    f"SlavStocks(tm).")
                self.cursor.execute("UPDATE players SET in_game='no', balance=?, net=? WHERE user=?",
                                    (entry[1] - bet, entry[2] - bet, str(gamer)))
                self.cursor.execute("SELECT * FROM blackjack WHERE user=?", (str(gamer),))
                temp = self.cursor.fetchone()
                self.cursor.execute("UPDATE blackjack SET games=?, gains=? WHERE user=?",
                                    (temp[1] + 1, temp[2] - bet, str(gamer)))
                self.database.commit()
                del player_bets[gamer]
                del player_decks[gamer]
                del dealt_hands[gamer]
                return
            else:
                await message.channel.send(f"Your score is {value}. You may now stand or hit.")
                dealt_hands[gamer] = hand
                player_decks[gamer] = deck
        elif message.content.lower() == "stand":
            hand = dealt_hands[gamer]
            value = calculate_value(hand)
            bet = player_bets[gamer]
            self.cursor.execute("SELECT * FROM players WHERE user=?", (str(gamer),))
            entry = self.cursor.fetchone()
            if value == 20:
                winnings = ceil(bet * 0.25)
                await message.channel.send(
                    f"You finished with a score of 20. You won {bet + winnings} SlavStocks(tm) and now have "
                    f"{entry[1] + winnings} SlavStocks(tm).")
            elif value == 19:
                winnings = ceil(bet * 0.05)
                await message.channel.send(
                    f"You finished with a score of 19. You won {bet + winnings} SlavStocks(tm) and now have "
                    f"{entry[1] + winnings} SlavStocks(tm).")
            elif value > 15:
                winnings = 0
                await message.channel.send(
                    f"You finished with a score of {value}. You got your {bet} SlavStocks(tm) back and now have "
                    f"{entry[1]} SlavStocks(tm).")
            else:
                winnings = 0 - bet
                await message.channel.send(
                    f"You finished with a score of {value}. You lost all {bet} SlavStocks(tm) :( You now have "
                    f"{entry[1] - bet} SlavStocks(tm).")
            self.cursor.execute("UPDATE players SET in_game='no', balance=?, net=? WHERE user=?",
                                (entry[1] + winnings, entry[2] + winnings, str(gamer)))
            self.cursor.execute("SELECT * FROM blackjack WHERE user=?", (str(gamer),))
            temp = self.cursor.fetchone()
            self.cursor.execute("UPDATE blackjack SET games=?, gains=? WHERE user=?",
                                (temp[1] + 1, temp[2] + winnings, str(gamer)))
            self.database.commit()
            del player_bets[gamer]
            del player_decks[gamer]
            del dealt_hands[gamer]


def setup(bot):
    bot.add_cog(Gamble(bot))
