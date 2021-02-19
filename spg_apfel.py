import PySimpleGUI as sg
import cmath
import numpy as np
from PIL import Image

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
                        graph_top_right=(500, 500),
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
            re_res, im_res = 500, 500
            max_iter = 100
            thresh = 100

            win['-TXT-'].update('started')
            a = calc(re_min, re_max, im_min, im_max, re_res, im_res, max_iter, thresh, win)
            win['-TXT-'].update('finished')


            data = a
            # Rescale to 0-255 and convert to uint8
            rescaled = (255.0 / data.max() * (data - data.min())).astype(np.uint8)
            im = Image.fromarray(rescaled)
            im.save('test.png')

            graph.draw_image('test.png', location=(0, 500))


if __name__ == '__main__':
    main()


