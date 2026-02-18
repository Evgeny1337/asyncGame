import random
import time
import curses
from explosion import explode
from game_scenario import  get_garbage_delay_tics
from utils import load_frames, load_garbage_frames, sleep
from constants import SUBWINDOW_HEIGHT, SUBWINDOW_WIDTH
from game_state import game_state
from game_mechanics import (
    year_counter, fire, fly_garbage, animate_spaceship
)
from ui import draw_subwindow, show_gameover, generate_stars

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


async def fill_orbit_with_garbage(coroutines, canvas, max_x, garbage_frames):
    while True:
        delay = get_garbage_delay_tics(game_state.year)
        
        if delay is None:
            await sleep(10)
            continue
            
        await sleep(delay)

        garbage_count = 0
        for coroutine in coroutines:
            if coroutine.__name__ == 'fly_garbage':
                garbage_count += 1
        
        if garbage_count < 5:  
            garbage_frame = random.choice(garbage_frames)
            garbage_column = random.randint(1, max_x - 1)
            garbage_coroutine = fly_garbage(canvas, garbage_column, garbage_frame)
            coroutines.append(garbage_coroutine)





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
        for obstacle in game_state.obstacles:
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





def draw(canvas):
    coroutines = []
    
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    canvas.keypad(True)
    canvas.nodelay(True)
    
    canvas.clear()
    canvas.border()
    canvas.refresh()
    
    max_y, max_x = canvas.getmaxyx()
    max_y -= 2
    max_x -= 2
    centre_x = max_x // 2 
    centre_y = max_y // 2
    
    ship_frames = load_frames()
    garbage_frames = load_garbage_frames()
    coordinates = {'column': centre_x, "row": centre_y, "space": False}


    exclusion_zone = {
        'begin_y': max_y + 2 - SUBWINDOW_HEIGHT - 1,
        'begin_x': max_x + 2 - SUBWINDOW_WIDTH - 1,
        'end_y': max_y + 2 - 1,
        'end_x': max_x + 2 - 1
    }

    coroutines = generate_stars(canvas, max_y, max_x, exclusion_zone)

    year_coroutine = year_counter()
    score_coroutine = draw_subwindow(canvas, game_state)
    garbage_coroutine = fill_orbit_with_garbage(coroutines, canvas, max_x, garbage_frames)
    spaceship_coroutine = run_spaceship(coroutines, canvas, coordinates, ship_frames)


    coroutines.extend([
        garbage_coroutine, 
        spaceship_coroutine, 
        score_coroutine,
        year_coroutine
    ])

    canvas.clear()

    while True:
        canvas.border()
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