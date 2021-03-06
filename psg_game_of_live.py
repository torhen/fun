import PySimpleGUI as sg
import random

X_DIM, Y_DIM = 50, 50
SCALE = 10
SHOW_EMPTY_CELLS = 0


def make_grid(x, y, kind):
    grid = []
    for j in range(x):
        row = []
        for _ in range(y):
            v = 0
            if kind == 'random':
                v = random.randint(0, 1)
            row.append(v)

        grid.append(row)
    return grid


def add_glider(grid):
    px, py = 0, 0
    grid[px + 0][py + 2] = 1
    grid[px + 1][py + 2] = 1
    grid[px + 2][py + 2] = 1
    grid[px + 2][py + 1] = 1
    grid[px + 1][py + 0] = 1


def add_spaceship(grid):
    px, py = 0, len(grid) // 2
    grid[px + 4][py + 3] = 1
    grid[px + 4][py + 2] = 1
    grid[px + 4][py + 1] = 1
    grid[px + 3][py + 0] = 1
    grid[px + 3][py + 3] = 1
    grid[px + 2][py + 3] = 1
    grid[px + 1][py + 3] = 1
    grid[px + 0][py + 2] = 1


def paint(graph, grid):
    graph.erase()
    for y in range(Y_DIM):
        for x in range(X_DIM):
            if grid[x][y] == 1:
                color = '#00aa00'
                graph.draw_rectangle((x, y), (x + 1, y + 1), fill_color=color)
            else:
                color = 'white'
                if SHOW_EMPTY_CELLS:
                    graph.draw_rectangle((x, y), (x + 1, y + 1), fill_color=color)


def get_item(grid, y, x, null_value):
    yl = len(grid)
    xl = len(grid[0])
    if y < 0 or x < 0:
        return null_value
    if y >= yl or x >= xl:
        return null_value
    return grid[y][x]


def sum_adj(grid, y, x):
    r = 0
    r = r + get_item(grid, y - 1, x - 1, 0)
    r = r + get_item(grid, y - 1, x, 0)
    r = r + get_item(grid, y - 1, x + 1, 0)

    r = r + get_item(grid, y, x - 1, 0)
    r = r + get_item(grid, y, x + 1, 0)

    r = r + get_item(grid, y + 1, x - 1, 0)
    r = r + get_item(grid, y + 1, x, 0)
    r = r + get_item(grid, y + 1, x + 1, 0)
    return r


def decide(v, nadj):
    assert v == 0 or v == 1, 'must be zero or one'
    if v == 0 and nadj == 3:
        return 1
    if v == 1 and nadj < 2:
        return 0
    if v == 1 and (nadj == 2 or nadj == 3):
        return 1
    if v == 1 and nadj > 3:
        return 0
    return 0


def develop(grid):
    # empty grid
    yl = len(grid)
    xl = len(grid[0])
    res = []
    for y in range(yl):
        row = []
        for x in range(xl):
            row.append(0)
        res.append(row)

    # set new values
    for y in range(yl):
        for x in range(xl):
            v = get_item(grid, y, x, -1)
            nadj = sum_adj(grid, y, x)
            v_new = decide(v, nadj)
            res[y][x] = v_new
    return res


def main():
    layout = [[
        sg.Button('start', key='-RUN-'),
        sg.Button('random', key='-RAN-'),
        sg.Button('clear', key='-CLEAR-'),
        sg.Button('glider', key='-GLI-'),
        sg.Button('spaceship', key='-SPA-'),
        sg.Slider(key='-TEMPO-',
                  range=(10, 1000), default_value=300,
                  orientation='horizontal',
                  enable_events=True, tooltip='interval in ms'),
    ],
        [sg.Graph(key='-GRA-', canvas_size=(X_DIM * SCALE, Y_DIM * SCALE),
                  graph_bottom_left=(0, 0),
                  graph_top_right=(X_DIM, Y_DIM),
                  enable_events=True
                  )]]

    win = sg.Window('Game Of Live', layout, finalize=True)
    graph = win['-GRA-']  # type:sg.Graph

    # initialize grid
    grid = make_grid(X_DIM, Y_DIM, 'zeros')
    paint(graph, grid)

    run = 0
    timeout = 10
    while True:
        event, values = win.read(timeout=timeout)
        if event == sg.WIN_CLOSED:
            break
        elif event == '-RUN-':
            btn = win['-RUN-']
            if run == 0:
                run = 1
                btn.update('stop')
            else:
                run = 0
                btn.update('start')
        elif event == '__TIMEOUT__':
            if run:
                grid = develop(grid)
                paint(graph, grid)
        elif event == '-RAN-':
            grid = make_grid(X_DIM, Y_DIM, 'random')
            paint(graph, grid)
        elif event == '-CLEAR-':
            grid = make_grid(X_DIM, Y_DIM, 'zeros')
            paint(graph, grid)
        elif event == '-GLI-':
            add_glider(grid)
            paint(graph, grid)
        elif event == '-SPA-':
            add_spaceship(grid)
            paint(graph, grid)
        elif event == '-GRA-':  # Mouse click
            x, y = values['-GRA-']
            v = grid[x][y]
            if v == 0:
                grid[x][y] = 1
            else:
                grid[x][y] = 0
            paint(graph, grid)
        elif event == '-TEMPO-':
            timeout = values['-TEMPO-']
    win.close()


if __name__ == '__main__':
    main()
