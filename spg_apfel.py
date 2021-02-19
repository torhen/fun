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


def calc(re_min, re_max, im_min, im_max, re_res, im_res, max_iter, thresh, win):
    # create C plane
    C = c_plane(re_min, re_max, re_res, im_min, im_max, im_res)

    # create and int start values
    X = np.copy(C)
    X[:] = complex(0, 0)

    # area for number of iterations
    R = np.zeros(C.shape)
    R[:] = np.nan

    for i in range(max_iter):
        X = X * X + C
        B = abs(X) > thresh
        X[B] = 0

        R[np.isnan(R) & B] = i
        win['-TXT-'].update('iteration: ' + str(i))
        win.refresh()

    R[np.isnan(R)] = 0
    return R


def main():
    layout = [[sg.Button('run', key='-RUN-'), sg.Text('', key='-TXT-', size=(10,1))],
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

            re_min, re_max = -2, 1
            im_min, im_max = -1.5, 1.5
            re_res, im_res = 300, 300
            max_iter = 1000
            thresh = 1000

            win['-TXT-'].update('started')
            a = calc(re_min, re_max, im_min, im_max, re_res, im_res, max_iter, thresh, win)
            win['-TXT-'].update('finished')

            height, width = a.shape
            graph.change_coordinates((0, 0), (width, height))

            for y in range(height):
                for x in range(width):
                    v = int(a[y, x])
                    v = int(v * 2.5)
                    color = "#%02x%02x%02x" % (0, v, 255-v)
                    graph.draw_rectangle((x, y), (x+1, y+1),fill_color=color, line_color=color)


if __name__ == '__main__':
    main()


