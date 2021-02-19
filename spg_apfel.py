import PySimpleGUI as sg
import cmath
import numpy as np
from PIL import Image


def c_plane(re_min, re_max, re_steps, im_min, im_max, im_steps):
    ar = []

    for im in np.linspace(im_max, im_min, im_steps):
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


def make_png(win, x_size, y_size, middle, radius, png_file):

    re_min, re_max = middle[0] - radius, middle[0] + radius
    im_min, im_max = middle[1] - radius, middle[1] + radius
    max_iter = 100
    thresh = 100

    win['-TXT-'].update('calculation started')
    a = calc(re_min, re_max, im_min, im_max, x_size, y_size, max_iter, thresh, win)
    win['-TXT-'].update('calculation finished')

    data = a
    # Rescale to 0-255 and convert to uint8
    rescaled = (255.0 / data.max() * (data - data.min())).astype(np.uint8)
    im = Image.fromarray(rescaled)
    im.save(png_file)


def main():
    X_SIZE = 800
    Y_SIZE = 800
    layout = [[
                sg.Button('Zoom out', key='-ZOOMOUT-'),
                sg.Text('', key='-TXT-', size=(20, 1)),
                sg.Text('', key='-COORD-', size=(50, 1))
               ],
              [sg.Graph(key='-GRAPH-',
                        graph_bottom_left=(0, 0),
                        graph_top_right=(X_SIZE, Y_SIZE),
                        canvas_size=(X_SIZE, Y_SIZE),
                        enable_events=True)
                        ]]

    win = sg.Window('Apfel', layout, finalize=True)
    graph = win['-GRAPH-'] # type:sg.Graph

    middle = [-0.7, 0]
    radius = 1.5

    win['-COORD-'].update(f'{middle} {radius}')
    make_png(win, X_SIZE, Y_SIZE, middle, radius, 'tmp.png')
    graph.draw_image('tmp.png', location=(0, Y_SIZE))

    while True:
        event, values = win.read()
        if event is None:
            break
        elif event == '-RUN-':
            win['-COORD-'].update(f'{middle} {radius}')
            make_png(win, X_SIZE, Y_SIZE, middle, radius, 'tmp.png')
            graph.draw_image('tmp.png', location=(0, Y_SIZE))

        elif event == '-GRAPH-':

            x_mouse, y_mouse = values['-GRAPH-']


            # bring to cordsystem -1..1
            x_norm = x_mouse * 2 / (X_SIZE-1) - 1.0
            y_norm = y_mouse * 2 / (Y_SIZE-1) - 1.0

            middle[0] = middle[0] + x_norm * radius
            middle[1] = middle[1] + y_norm * radius
            radius = radius / 2

            win['-COORD-'].update(f'{middle} {radius}')
            make_png(win, X_SIZE, Y_SIZE, middle, radius, 'tmp.png')
            graph.draw_image('tmp.png', location=(0, Y_SIZE))
        elif event == '-ZOOMOUT-':
            radius = radius * 2

            make_png(win, X_SIZE, Y_SIZE, middle, radius, 'tmp.png')
            graph.draw_image('tmp.png', location=(0, Y_SIZE))


if __name__ == '__main__':
    main()


