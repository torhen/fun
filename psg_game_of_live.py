import PySimpleGUI as sg
import random

XDIM, YDIM = 50, 50
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

    # glider
    if kind == 'glider':
        px, py = 10, 20
        grid[px + 0][py + 0] = 1
        grid[px + 1][py + 0] = 1
        grid[px + 2][py + 0] = 1
        grid[px + 2][py + 1] = 1
        grid[px + 1][py + 2] = 1

    return grid

def paint(graph, grid):
    graph.erase()
    for y in range(YDIM):
        for x in range(XDIM):
            if grid[x][y] == 1:
                color = '#00aa00'
                graph.draw_rectangle( (x,y), (x+1, y+1), fill_color=color)
            else:
                color = 'white'
                if SHOW_EMPTY_CELLS:
                    graph.draw_rectangle( (x,y), (x+1, y+1), fill_color=color)

            

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
    r = r + get_item(grid, y-1, x-1, 0)
    r = r + get_item(grid, y-1,   x, 0)
    r = r + get_item(grid, y-1, x+1, 0)

    r = r + get_item(grid, y, x-1, 0)
    r = r + get_item(grid, y, x+1, 0)

    r = r + get_item(grid, y+1, x-1, 0)
    r = r + get_item(grid, y+1,   x, 0)
    r = r + get_item(grid, y+1, x+1, 0)
    return r

def decide(v, nadj):
    assert v == 0 or v == 1, 'must be zero or one'
    if v == 0 and nadj == 3:
        return 1
    if v == 1 and nadj < 2:
        return 0
    if v == 1 and (nadj ==2 or nadj == 3):
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

# -------------- G U I -------------------

layout = [[
            sg.Button('start', key='-RUN-'), 
            sg.Button('random', key='-RAN-'),
            sg.Button('clear', key='-CLEAR-'), 
            sg.Button('glider', key='-GLI-')           
            ],
          [sg.Graph(key='-GRA-', canvas_size=(XDIM * SCALE,YDIM * SCALE),
                    graph_bottom_left=(0,0),
                    graph_top_right=(XDIM, YDIM),
                    enable_events = True
                    )]]


win = sg.Window('test', layout, finalize=True)
graph = win['-GRA-'] # type:sg.Graph

# initialize grid
grid = make_grid(XDIM, YDIM, 'zeros')
paint(graph, grid)

run = 0
while True:
    event, values = win.read(timeout=10)
    if event == None:
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
        grid = make_grid(XDIM, YDIM, 'random')
        paint(graph, grid)
    elif event == '-CLEAR-':
        grid = make_grid(XDIM, YDIM, 'zeros')
        paint(graph, grid)
    elif event == '-GLI-':
        grid = make_grid(XDIM, YDIM, 'glider')
        paint(graph, grid)
    elif event == '-GRA-': # Mouse click
        x, y = values['-GRA-']
        v = grid[x][y]
        if v == 0:
            grid[x][y] = 1
        else:
            grid[x][y] = 0
        paint(graph, grid)

win.close()