import PySimpleGUI as sg
import cmath
import numpy as np


def c_plane(re_min, re_max, re_steps, im_min, im_max, im_steps):
    ar = []

    for im in np.linspace(im_min, im_max, im_steps):
        row = []
        for re in np.linspace(re_min, re_max, re_steps):
            v = complex(re, im)
            row.append(v)
        ar.append(row)

    return np.array(ar)


def calc(re_min, re_max, im_min, im_max, re_res, im_res, max_iter, thresh):
    C = c_plane(re_min, re_max, re_res, im_min, im_max, im_res)
    X = np.copy(C)
    X[:] = complex(0, 0)

    R = np.zeros(C.shape)
    R[:] = np.nan

    for i in range(max_iter):
        X = X**2 + C
        B = X > thresh

        R[np.isnan(R) & B] = i
    R[np.isnan(R)] = 0
    return R


def main():
    re_min, re_max = -2, 1
    im_min, im_max = -1.5, 1.5
    re_res, im_res = 200, 200
    max_iter = 100
    thresh = 100

    layout = [[sg.Button('run', key='-RUN-')],
              [sg.Graph(key='-GRAPH-',
                        graph_bottom_left=(0, 0),
                        graph_top_right=(100, 100),
                        canvas_size=(500, 500))
                        ]]

    win = sg.Window('Apfel', layout)

    graph = win['-GRAPH-'] # type:sg.Graph

    while True:
        event, values = win.read()
        if event is None:
            break
        elif event == '-RUN-':
            a = calc(re_min, re_max, im_min, im_max, re_res, im_res, max_iter, thresh)
            height, width = a.shape
            graph.change_coordinates((0,0), (width, height))

            for y in range(height):
                for x in range(width):
                    v = int(a[y, x])
                    v = int(v * 2.5)
                    color = "#%02x%02x%02x" % (v, 0, 255-v)
                    graph.draw_rectangle((x, y), (x+1, y+1),fill_color=color, line_color=color)


if __name__ == '__main__':
    main()


