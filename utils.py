import os
import asyncio
import curses


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines], default=0)
    return rows, columns

def draw_frame(canvas, start_row, start_column, text, negative=False):
    rows_number, columns_number = canvas.getmaxyx()
    
    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0 or row >= rows_number:
            continue
            
        for column, symbol in enumerate(line, round(start_column)):
            if column < 0 or column >= columns_number:
                continue
            if symbol == ' ':
                continue
            if row == rows_number - 1 and column == columns_number - 1:
                continue
                
            symbol = symbol if not negative else ' '
            try:
                canvas.addstr(row, column, symbol)
            except curses.error:
                pass

def load_frames():
    try:
        with open('./steps/step_1.txt', 'r') as file_1:
            frame_1 = file_1.read()
        with open('./steps/step_2.txt', 'r') as file_2:
            frame_2 = file_2.read()
        return frame_1, frame_1, frame_2, frame_2
    except FileNotFoundError:
        return []

def load_garbage_frames():
    garbage_frames = []
    if os.path.exists('./pictures'):
        for file in os.listdir('./pictures'):
            if file.endswith('.txt'):
                file_path = os.path.join('./pictures', file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            garbage_frames.append(content)
                except Exception:
                    continue
    
    return garbage_frames

async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)

def read_controls(canvas):
    from constants import SPACE_KEY_CODE, LEFT_KEY_CODE, RIGHT_KEY_CODE, UP_KEY_CODE, DOWN_KEY_CODE
    
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