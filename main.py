import time
import curses
import asyncio

async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

def draw(canvas):
    row, column = (5, 20)
    canvas.border()
    curses.noecho()
    curses.cbreak()
    canvas.keypad(True)
    while True:
        canvas.addstr(row, column, "*",   curses.A_DIM)
        canvas.refresh()
        time.sleep(2)
        canvas.addstr(row, column, "*")
        canvas.refresh()
        time.sleep(0.3)
        canvas.addstr(row, column, "*", curses.A_BOLD)
        canvas.refresh()
        time.sleep(0.5)
        canvas.addstr(row, column, "*")
        canvas.refresh()
        time.sleep(0.3)







if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
    curses.curs_set(False)