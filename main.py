import os
import random
import time
import curses
import asyncio
from itertools import cycle
from physics import update_speed
from obstacles import Obstacle, show_obstacles
from explosion import explode

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

OBSTACLES = []
OBSTACLES_IN_LAST_COLLISIONS = []


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def show_gameover(canvas):
    gameover_art = """
   _____                         ____                 
  / ____|                       / __ \\                
 | |  __  __ _ _ __ ___   ___  | |  | |_   _____ _ __ 
 | | |_ |/ _` | '_ ` _ \\ / _ \\ | |  | \\ \\ / / _ \\ '__|
 | |__| | (_| | | | | | |  __/ | |__| |\\ V /  __/ |   
  \\_____|\\__,_|_| |_| |_|\\___|  \\____/  \\_/ \\___|_|   
    """
    while True:
        height, width = canvas.getmaxyx()
        lines = gameover_art.splitlines()
        
        start_row = height // 2 - len(lines) // 2
        
        for i, line in enumerate(lines):
            if line.strip():
                start_col = width // 2 - len(line) // 2
                canvas.addstr(start_row + i, start_col, line, curses.A_BOLD)
        
        canvas.refresh()
        await sleep(1)


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
        for obstacle in OBSTACLES:
            if obstacle.has_collision(round(row), round(column)):
                OBSTACLES_IN_LAST_COLLISIONS.append(obstacle)
                await explode(canvas, round(row), round(column), get_frame_size, draw_frame)
                return
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
    frame_height, frame_width = get_frame_size(garbage_frame)

    obstacle = Obstacle(row, column, frame_height, frame_width)
    OBSTACLES.append(obstacle)
    
    while row < rows_number:
        if obstacle in OBSTACLES_IN_LAST_COLLISIONS:
            OBSTACLES.remove(obstacle)
            OBSTACLES_IN_LAST_COLLISIONS.remove(obstacle)
            return
        
        obstacle.row = round(row)
        draw_frame(canvas, row, column, garbage_frame)
        await sleep(1)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed

    if obstacle in OBSTACLES:
        OBSTACLES.remove(obstacle)


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
    with open('./steps/step_1.txt', 'r') as file_1:
        frame_1 = file_1.read()
    with open('./steps/step_2.txt', 'r') as file_2:
        frame_2 = file_2.read()
    return frame_1, frame_1, frame_2, frame_2


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


async def animate_spaceship(canvas, start_row, start_column, frames, coordinates, ship_alive):
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
        if not ship_alive[0]:
            draw_frame(canvas, row, column, current_frame, negative=True)
            return
            
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)

        coordinates["space"] = space_pressed

        new_row = row + row_speed
        new_column = column + column_speed

        if min_row <= new_row <= max_row and min_col <= new_column <= max_col:
            if row != new_row or column != new_column:
                draw_frame(canvas, row, column, current_frame, negative=True)
                row, column = new_row, new_column

        draw_frame(canvas, row, column, current_frame, negative=True)
        current_frame = next(frame_cycle)
        draw_frame(canvas, row, column, current_frame)

        coordinates["row"], coordinates["column"] = row, column
        await sleep(1)


async def run_spaceship(coroutines, canvas, coordinates, frames):
    ship_height, ship_width = get_frame_size(frames[0])
    
    burst_count = 0  
    burst_size = 3   
    shot_cooldown = 0  
    burst_cooldown = 0  
    ship_alive = [True]
    game_over_shown = False
    
    rocket_coroutine = animate_spaceship(canvas, coordinates["row"], coordinates["column"], frames, coordinates, ship_alive)
    coroutines.append(rocket_coroutine)
    
    while True:
        for obstacle in OBSTACLES:
            if obstacle.has_collision(
                coordinates["row"], 
                coordinates["column"], 
                ship_height, 
                ship_width
            ) and ship_alive[0]:
                ship_alive[0] = False
                await explode(canvas, coordinates["row"], coordinates["column"], get_frame_size, draw_frame)
                
        if not ship_alive[0] and not game_over_shown:
            canvas.clear()
            canvas.border()
            for coroutine in coroutines:
                if coroutine != rocket_coroutine:
                    try:
                        coroutine.send(None)
                    except:
                        pass
            await show_gameover(canvas)
            game_over_shown = True
            canvas.refresh()
            await sleep(50)
            return
            
        await sleep(1)

        if coordinates["space"] and burst_cooldown <= 0 and burst_count == 0 and ship_alive[0]:
            burst_count = burst_size 
            shot_cooldown = 0  

        if burst_count > 0 and shot_cooldown <= 0 and ship_alive[0]:
            fire_coroutine = fire(canvas, coordinates["row"], coordinates["column"], -1)
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
    
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    canvas.bkgd(' ', curses.color_pair(1))
    
    canvas.clear()
    canvas.border()
    canvas.refresh()
    
    y, x = curses.window.getmaxyx(canvas)
    y = y - 2
    x = x - 2

    max_star = random.randint(1, x*y) // 10
    centre_x = x // 2 
    centre_y = y // 2
    
    frames = load_frames()
    coordinates = {'column': centre_x, "row": centre_y, "space": False}

    garbage_coroutine = fill_orbit_with_garbage(garbage_coroutines, canvas, x)
    fire_spaceship_coroutine = run_spaceship(coroutines, canvas, coordinates, frames)
    obstacle_coroutine = show_obstacles(draw_frame, canvas, OBSTACLES)

    coroutines.extend([
        garbage_coroutine, 
        fire_spaceship_coroutine, 
        obstacle_coroutine
    ])

    for _ in range(max_star):
        x_star = random.randint(1, x)
        y_star = random.randint(1, y)
        symbol = random.choice(symbols)
        offset_tics = [random.randint(1, 20) for _ in range(4)]
        coroutine = blink(canvas, y_star, x_star, offset_tics, symbol)
        coroutines.append(coroutine)

    canvas.clear()
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