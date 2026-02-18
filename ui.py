import curses
import random
from game_scenario import PHRASES
from utils import sleep
from constants import STARS_SYMBOLS, SUBWINDOW_HEIGHT, SUBWINDOW_WIDTH


async def draw_subwindow(canvas, game_state):
    max_y, max_x = canvas.getmaxyx()
    begin_y = max_y - SUBWINDOW_HEIGHT - 1 
    begin_x = max_x - SUBWINDOW_WIDTH - 1
    
    current_year = 1957
    
    while True:
        subwin = canvas.derwin(SUBWINDOW_HEIGHT, SUBWINDOW_WIDTH, begin_y, begin_x)
        subwin.border()
        
        if game_state.year in PHRASES:
            current_year = game_state.year
        try:
            subwin.addstr(3, 1, " " * 18)
            subwin.addstr(3, 1, PHRASES.get(current_year, "Unknown")[:18])
        except curses.error:
            pass
            
        subwin.refresh()
        await sleep(1)

async def show_gameover(canvas):
    gameover_art = """
   _____                         ____                 
  / ____|                       / __ \\                
 | |  __  __ _ _ __ ___   ___  | |  | |_   _____ _ __ 
 | | |_ |/ _` | '_ ` _ \\ / _ \\ | |  | \\ \\ / / _ \\ '__|
 | |__| | (_| | | | | | |  __/ | |__| |\\ V /  __/ |   
  \\_____|\\__,_|_| |_| |_|\\___|  \\____/  \\_/ \\___|_|   
    """
    height, width = canvas.getmaxyx()
    lines = gameover_art.splitlines()
    start_row = height // 2 - len(lines) // 2
    
    for i, line in enumerate(lines):
        if line.strip():
            start_col = width // 2 - len(line) // 2
            try:
                canvas.addstr(start_row + i, start_col, line, curses.A_BOLD)
            except curses.error:
                pass
    
    canvas.refresh()
    await sleep(50)

async def blink(canvas, row, column, offset_tics, symbol='*'):
    while True:
        try:
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
        except curses.error:
            await sleep(1)

def generate_stars(canvas, max_y, max_x, exclusion_zone):
    coroutines = []
    max_star = random.randint(1, max_x * max_y) // 10
    stars_generated = 0
    max_attempts = max_star * 10
    
    while stars_generated < max_star and max_attempts > 0:
        max_attempts -= 1 
        
        x_star = random.randint(1, max_x)
        y_star = random.randint(1, max_y)
        
        if not (exclusion_zone['begin_y'] <= y_star < exclusion_zone['end_y'] and 
                exclusion_zone['begin_x'] <= x_star < exclusion_zone['end_x']):
            symbol = random.choice(STARS_SYMBOLS)
            offset_tics = [random.randint(1, 20) for _ in range(4)]
            coroutine = blink(canvas, y_star, x_star, offset_tics, symbol)
            coroutines.append(coroutine)
            stars_generated += 1
    
    return coroutines