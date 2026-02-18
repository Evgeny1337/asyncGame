import curses
import asyncio
from itertools import cycle
from physics import update_speed
from obstacles import Obstacle
from explosion import explode
from utils import get_frame_size, draw_frame, sleep, read_controls
from game_state import game_state  

async def year_counter():
    frames_per_year = 40
    frame_count = 0
    
    while True:
        if frame_count >= frames_per_year:
            game_state.year += 1
            frame_count = 0
            if game_state.year >= 2020:
                game_state.speed_multiplier = 2.0
            elif game_state.year >= 2011:
                game_state.speed_multiplier = 1.8
            elif game_state.year >= 1998:
                game_state.speed_multiplier = 1.6
            elif game_state.year >= 1981:
                game_state.speed_multiplier = 1.4
            elif game_state.year >= 1969:
                game_state.speed_multiplier = 1.2
        
        frame_count += 1
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
        for obstacle in game_state.obstacles:
            if obstacle.has_collision(round(row), round(column)):
                game_state.obstacles_in_last_collisions.append(obstacle)
                await explode(canvas, round(row), round(column), get_frame_size, draw_frame)
                return
                
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed

async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    rows_number, columns_number = canvas.getmaxyx()
    column = max(column, 0)
    column = min(column, columns_number - 1)
    row = 0
    
    frame_height, frame_width = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, frame_height, frame_width)
    game_state.obstacles.append(obstacle)
    
    while row < rows_number:
        if obstacle in game_state.obstacles_in_last_collisions:
            game_state.obstacles.remove(obstacle)
            game_state.obstacles_in_last_collisions.remove(obstacle)
            return
        
        obstacle.row = round(row)
        draw_frame(canvas, row, column, garbage_frame)
        await sleep(1)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed

    if obstacle in game_state.obstacles:
        game_state.obstacles.remove(obstacle)

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
    
    draw_frame(canvas, row, column, current_frame)
    
    while True:
        if not ship_alive[0]:
            draw_frame(canvas, row, column, current_frame, negative=True)
            return
            
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row_speed, column_speed = update_speed(
            row_speed, column_speed, 
            rows_direction, columns_direction,
            row_speed_limit=2, column_speed_limit=2
        )

        coordinates["space"] = space_pressed
        new_row = row + row_speed
        new_column = column + column_speed

        draw_frame(canvas, row, column, current_frame, negative=True)

        if (min_row <= new_row <= max_row and 
            min_col <= new_column <= max_col):
            row, column = new_row, new_column

        current_frame = next(frame_cycle)
        draw_frame(canvas, row, column, current_frame)

        coordinates["row"], coordinates["column"] = row, column
        await sleep(1)