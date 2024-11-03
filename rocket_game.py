import asyncio
import curses
import random
import time

from curses_tools import draw_frame, read_controls

TIC_TIMEOUT = 0.1
STARS_COUNT = 100
STARTS_SIMBOLS = '+*.:'
BOARD_SIZE = 2


def load_rocket():
    rocket_frames = []
    for file in ["rocket_frame_1.txt", "rocket_frame_2.txt"]:
        with open(file, 'r', encoding='UTF-8') as file:
            rocket_frames.append(file.read())
    return rocket_frames


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for i in range(random.randint(1, 25)):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        for i in range(random.randint(1, 5)):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(random.randint(1, 6)):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        for i in range(random.randint(1, 5)):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

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

    while BOARD_SIZE < row < max_row and BOARD_SIZE < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, row, column, frames):
    while True:
        for frame in frames:
            row, column = get_rocket_position(canvas, row, column, controls, frame)
            draw_frame(canvas, row, column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, frame, negative=True)


def get_rocket_position(canvas, current_row, current_column, controls, frame):
    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - BOARD_SIZE, columns - BOARD_SIZE
    frame_rows, frame_columns = get_frame_size(frame)
    controls_row, controls_column, _ = controls
    row, column = current_row + controls_row, current_column + controls_column
    row = max(BOARD_SIZE, min(row, max_row - frame_rows))
    column = max(BOARD_SIZE, min(column, max_column - frame_columns))
    return row, column


def get_frame_size(frame):
    lines = frame.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def draw(canvas):
    global controls
    rocket_frames = load_rocket()
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    rows, columns = canvas.getmaxyx()
    coroutines = [
        blink(canvas, random.randint(1, rows - BOARD_SIZE),
              random.randint(1, columns - BOARD_SIZE),
              random.choice(list(STARTS_SIMBOLS))) for _ in range(STARS_COUNT)
    ]

    coroutines.append(animate_spaceship(canvas,
                                        rows - 10,
                                        columns / 2 - 2,
                                        rocket_frames))

    coroutines.append(fire(canvas, rows / 2, columns / 2))

    while True:
        controls = read_controls(canvas)
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(TIC_TIMEOUT)
        canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
