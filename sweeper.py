from discord.ext import commands
import random

board_emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "💣"]


def make_board(size, bombs):
    board = [[0 for i in range(size)] for j in range(size)]
    mines = []
    while len(mines) < bombs:
        row = random.randint(0, size - 1)
        col = random.randint(0, size - 1)
        if (row, col) not in mines:
            board[col][row] = 9
            if (col - 1) >= 0 and (row - 1) >= 0:
                if board[col - 1][row - 1] != 9:
                    board[col - 1][row - 1] += 1
            if (col - 1) >= 0:
                if board[col - 1][row] != 9:
                    board[col - 1][row] += 1
            if (col - 1) >= 0 and (row + 1) < size:
                if board[col - 1][row + 1] != 9:
                    board[col - 1][row + 1] += 1
            if (row - 1) >= 0:
                if board[col][row - 1] != 9:
                    board[col][row - 1] += 1
            if (row + 1) < size:
                if board[col][row + 1] != 9:
                    board[col][row + 1] += 1
            if (col + 1) < size and (row - 1) >= 0:
                if board[col + 1][row - 1] != 9:
                    board[col + 1][row - 1] += 1
            if (col + 1) < size:
                if board[col + 1][row] != 9:
                    board[col + 1][row] += 1
            if (col + 1) < size and (row + 1) < size:
                if board[col + 1][row + 1] != 9:
                    board[col + 1][row + 1] += 1
            mines.append((row, col))
    return board


def display_board(board):
    board_string = ""
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[j][i] == 0:
                board_string += f"{board_emojis[board[j][i]]}"
            else:
                board_string += f"||{board_emojis[board[j][i]]}||"
        board_string += "\n"
    return board_string


class Sweeper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sweeper(self, ctx, size=9):
        if size < 4:
            await ctx.send("Too small.")
            return
        if size > 14:
            await ctx.send("Too big.")
            return
        bombs = (size*size)//8
        await ctx.send(display_board(make_board(size, bombs)))


def setup(bot):
    bot.add_cog(Sweeper(bot))
