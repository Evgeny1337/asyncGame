import os
import random
import time
import curses
import asyncio
from itertools import cycle
from physics import update_speed
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258
PREV_STATE_CODE = 0




async def sleep(tics=1):
    for _ in range(tics):
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

        


async def fill_orbit_with_garbage(coroutines, canvas, max_x):
    garbage_frames = []
    for file in os.listdir('./pictures'):
        if file.endswith('.txt'):
            file_path = os.path.join('./pictures', file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    garbage_frames.append(content)
            except Exception:
                continue
    
    while True:
        await sleep(4)
        if len(coroutines) < 5:  
            garbage_frame = random.choice(garbage_frames)
            garbage_column = random.randint(1, max_x - 1)
            garbage_coroutine = fly_garbage(canvas, garbage_column, garbage_frame)
            coroutines.append(garbage_coroutine)
   
        
        

async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    rows_number, columns_number = canvas.getmaxyx()
    column = max(column, 0)
    column = min(column, columns_number - 1)
    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await sleep(1)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns




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



def load_frames():
    file_1 = open('./steps/step_1.txt', 'r')
    frame_1 = file_1.read()
    file_1.close()
    file_2 = open('./steps/step_2.txt', 'r')
    frame_2 = file_2.read()
    file_2.close()
    return frame_1,frame_1,frame_2,frame_2

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




async def animate_spaceship(canvas, start_row, start_column, frames, coordinates):
    row, column = start_row, start_column
    rocket_height, rocket_width = get_frame_size(frames[0])
    screen_height, screen_width = canvas.getmaxyx()
    frame_cycle = cycle(frames)
    max_row = screen_height - rocket_height - 1
    max_col = screen_width - rocket_width - 1
    min_row = 1
    min_col = 1
    row_speed = column_speed = 0
    current_frame = next(frame_cycle)
    while True:
        
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)

        if space_pressed:
            coordinates["space"] = True
        else:
            coordinates["space"] = False

        new_row = row + row_speed
        new_column = column + column_speed

        
        if min_row <= new_row <= max_row and min_col <= new_column <= max_col:
            if row != new_row or column != new_column:
                draw_frame(canvas, row, column, current_frame, negative=True)
                row, column = new_row, new_column

        draw_frame(canvas, row, column, current_frame, negative=True)
        current_frame = next(frame_cycle)
        draw_frame(canvas, row, column, current_frame)

        coordinates["row"],coordinates["column"] = new_row, new_column
        

        await sleep(1)

async def fire_spaceship(coroutines, canvas, coordinates):
    burst_count = 0  
    burst_size = 3   
    shot_cooldown = 0  
    burst_cooldown = 0  
    
    while True:
        await sleep(1)

        if coordinates["space"] and burst_cooldown <= 0 and burst_count == 0:
            burst_count = burst_size 
            shot_cooldown = 0  

        if burst_count > 0 and shot_cooldown <= 0:

            fire_coroutine = fire(canvas, coordinates["row"], coordinates["column"])
            coroutines.append(fire_coroutine)
            
            burst_count -= 1  
            shot_cooldown = 3  

            if burst_count == 0:
                burst_cooldown = 15  

        if shot_cooldown > 0:
            shot_cooldown -= 1
        if burst_cooldown > 0:
            burst_cooldown -= 1


async def blink(canvas, row, column, offset_tics, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(offset_tics[0]):
            await sleep(1)

        canvas.addstr(row, column, symbol)
        for _ in range(offset_tics[1]):
            await sleep(1)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(offset_tics[2]):
            await sleep(1)

        canvas.addstr(row, column, symbol)
        for _ in range(offset_tics[3]):
            await sleep(1)
        
        

def draw(canvas):
    symbols = '+*.:'
    coroutines = []
    garbage_coroutines = []
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    canvas.keypad(True)
    canvas.nodelay(True)
    canvas.clear()
    canvas.border()
    canvas.refresh()
    y,x = curses.window.getmaxyx(canvas)
    y = y - 2
    x = x - 2

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    canvas.bkgd(' ', curses.color_pair(1))
    canvas.clear()

    max_star = random.randint(1,x*y)//10
    centre_x = x//2 
    centre_y = y//2
    frames = load_frames()
    coordinates = {'column':centre_x,"row":centre_y,"space":False}

    rocket_coroutine = animate_spaceship(canvas, centre_y, centre_x, frames, coordinates)
    garbage_coroutine = fill_orbit_with_garbage(garbage_coroutines, canvas, x)
    fire_spaceship_coroutine = fire_spaceship(coroutines, canvas, coordinates)

    coroutines.extend([rocket_coroutine, garbage_coroutine, fire_spaceship_coroutine])

    for _ in range(max_star):
        x_star = random.randint(1, x)
        y_star = random.randint(1, y)
        symbol = random.choice(symbols)
        offset_tics = [random.randint(1, 20) for _ in range(4)]
        coroutine =  blink(canvas, y_star, x_star, offset_tics, symbol)
        coroutines.append(coroutine)


    while True:
        canvas.border()
        for coroutine in garbage_coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                garbage_coroutines.remove(coroutine)
                
        
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(0.1)
        canvas.refresh()
        


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)
    curses.curs_set(False)

if __name__ == '__main__':
    main()



