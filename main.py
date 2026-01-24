import random
import time
import curses
import asyncio
from itertools import cycle
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

file_1 = open('step_1.txt','r')
FRAME_1 = file_1.read()
file_1.close()
file_2 = open('step_2.txt','r')
FRAME_2 = file_2.read()
file_2.close()


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def read_controls(canvas):
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    rows_number, columns_number = canvas.getmaxyx()
    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addstr(row, column, symbol)


async def animate_spaceship(canvas, start_row, start_column, frames):
    row, column = start_row, start_column
    rocket_height, rocket_width = get_frame_size(frames[0])
    screen_height, screen_width = canvas.getmaxyx()
    frame_cycle = cycle(frames)
    max_row = screen_height - rocket_height - 1
    max_col = screen_width - rocket_width - 1
    min_row = 1
    min_col = 1
    current_frame = next(frame_cycle)
    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        new_row = row + rows_direction
        new_column = column + columns_direction
        if min_row <= new_row <= max_row and min_col <= new_column <= max_col:
            draw_frame(canvas, row, column, current_frame, negative=True)
            row, column = new_row, new_column

        draw_frame(canvas, row, column, current_frame, True)
        current_frame = next(frame_cycle)
        draw_frame(canvas, row, column, current_frame)

        for _ in range(2):
            await asyncio.sleep(0)






async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    row, column = start_row, start_column
    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed

async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        ticks = [random.randint(1,20) for _ in range(4)]
        for _ in range(ticks[0]):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(ticks[1]):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(ticks[2]):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(ticks[3]):
            await asyncio.sleep(0)

def draw(canvas):
    symbols = '+*.:'
    coroutines = []
    canvas.border()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    canvas.keypad(True)
    canvas.nodelay(True)
    y,x = curses.window.getmaxyx(canvas)
    y = y - 2
    x = x - 2
    max_star = random.randint(1,x*y)
    rows_direction, columns_direction, space_pressed = 0,0,0
    centre_x = x//2 + rows_direction
    centre_y = y//2 + columns_direction
    frames = [FRAME_1, FRAME_2]
    rocket_coroutine = animate_spaceship(canvas, centre_y, centre_x, frames)
    for _ in range(max_star):
        x_star = random.randint(1, x)
        y_star = random.randint(1, y)
        symbol = random.choice(symbols)
        coroutine =  blink(canvas, y_star, x_star, symbol)
        coroutines.append(coroutine)
    coroutines.append(rocket_coroutine)
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(0.1)
        canvas.refresh()



if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
    curses.curs_set(False)



