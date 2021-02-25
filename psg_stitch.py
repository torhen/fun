import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageOps
import pathlib
import PySimpleGUI as sg


def get_width_height(img_file: str):
    """get dimension of a imgage file"""
    img = Image.open(img_file)
    w, h = img.size
    return (w, h)


def crop(img_file: str, top_left: tuple, width_height: int, dest_file: str):
    """crops image file"""
    if not pathlib.Path(img_file).is_file():
        print('not found', img_file)
        return
    img = Image.open(img_file)
    crop = img.crop((top_left[0], top_left[1], width_height[0], width_height[1]))
    crop.save(dest_file)


def side_by_side(img_file1, img_file2, result):
    """show tmplate and match on same pic to compare"""
    img1 = Image.open(img_file1)
    img2 = Image.open(img_file2)

    # caluculate result dimensions
    w1, h1 = img1.size
    w2, h2 = img2.size

    if w1 < h1:
        side = True
    else:
        side = False

    if side:
        new_im = Image.new('RGB', (w1 + w2, h1))
        new_im.paste(img1, (0, 0))
        new_im.paste(img2, (w1, 0))
    else:
        # unereinander
        new_im = Image.new('RGB', (w1, h1 + h2))
        new_im.paste(img1, (0, 0))
        new_im.paste(img2, (0, h1))

    new_im.save(result)


def match(img_file: str, template_file: str, template_origin: 'only for naming comp png'):
    """get the position of template"""
    img_file = str(img_file)
    template_file = str(template_file)
    img = cv2.imread(img_file, cv2.IMREAD_COLOR)
    tpl = cv2.imread(template_file, cv2.IMREAD_COLOR)
    h, w, channels = tpl.shape

    res = cv2.matchTemplate(img, tpl, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # min_loc for SQARE_ALORTIHM
    top_left_found = min_loc
    xs, ys = top_left_found

    match_img = img[ys: ys + h, xs:xs + w]
    cv2.imwrite('tmp/match.png', match_img)

    # name for compare file
    stem1 = pathlib.Path(img_file).stem
    stem2 = pathlib.Path(template_origin).stem
    comp_path = f"tmp/comp_{stem1}_{stem2}.png"
    g_compare_images.append(comp_path)

    side_by_side('tmp/templ.png', 'tmp/match.png', comp_path)


def stitch_right(map_left: str, map_right: str, anker: tuple, map_result: str, gray=False):
    """merge to files using anker coordinate
cut of black areas
    """
    # do with PIL!
    img1 = Image.open(map_left)
    img2 = Image.open(map_right)

    # make gray for checking
    if gray:
        img2 = ImageOps.grayscale(img2)

    # caluculate result dimensions
    w1, h1 = img1.size
    w2, h2 = img2.size

    hr = h1  # make result height like image1
    wr = anker[0] + w2  # - anker[0] # both widths minus overlapping

    new_im = Image.new('RGB', (wr, hr))
    new_im.paste(img1, (0, 0))
    new_im.paste(img2, anker)

    # calc overlapping y range
    if anker[1] > 0:
        left, right = 0, wr  # width no change
        top = anker[1]
        bottom = min(h1, anker[1] + h2)
        new_im = new_im.crop((left, top, right, bottom))
    else:
        left, right = 0, wr
        top = 0
        bottom = min(h1, anker[1] + h2)
        new_im = new_im.crop((left, top, right, bottom))
    new_im.save(map_result)


def match(img_file: str, template_file: str, template_origin: 'only for naming comp png'):
    """get the position of template"""
    img_file = str(img_file)
    template_file = str(template_file)
    img = cv2.imread(img_file, cv2.IMREAD_COLOR)
    tpl = cv2.imread(template_file, cv2.IMREAD_COLOR)
    h, w, channels = tpl.shape

    res = cv2.matchTemplate(img, tpl, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # min_loc for SQARE_ALORTIHM
    top_left_found = min_loc
    xs, ys = top_left_found

    match_img = img[ys: ys + h, xs:xs + w]
    cv2.imwrite('tmp/match.png', match_img)

    # name for compare file
    stem1 = pathlib.Path(img_file).stem
    stem2 = pathlib.Path(template_origin).stem
    comp_path = f"tmp/comp_{stem1}_{stem2}.png"
    g_compare_images.append(comp_path)

    side_by_side('tmp/templ.png', 'tmp/match.png', comp_path)

    return top_left_found


def extend_one_right(img1: str, img2: str, res: str, gray=False):
    """extend to images to the right"""
    w1, h1 = get_width_height(img1)
    w2, h2 = get_width_height(img2)
    # print('dimensions of img1 and img2', (w1, h1), (w2, h2) )

    # crop out the template
    wt = 100
    ht = h2 // 2
    x0 = 0
    y0 = ht // 4
    crop(img2, (x0, y0), (wt, ht), 'tmp/templ.png')

    # template matching
    top_left_found = match(img1, 'tmp/templ.png', img2)
    anker = (top_left_found[0], top_left_found[1] - y0)  # template start not at (0, 0)
    # print('found anker point', anker)

    # stich images
    stitch_right(img1, img2, anker, res, gray)


def extend_right(images: [], result: str):
    # first image
    extend_one_right(images[0], images[1], result)

    for img in images[2:]:
        extend_one_right(result, img, result)


def stitch_down(map_left: str, map_right: str, anker: tuple, map_result: str, gray=False):
    """merge to files using anker coordinate
cut of black areas
    """
    # do with PIL!
    img1 = Image.open(map_left)
    img2 = Image.open(map_right)

    # make gray for checking
    if gray:
        img2 = ImageOps.grayscale(img2)

    # caluculate result dimensions
    w1, h1 = img1.size
    w2, h2 = img2.size

    wr = anker[0] + w2
    hr = anker[1] + h2

    new_im = Image.new('RGB', (wr, hr))
    new_im.paste(img1, (0, 0))
    new_im.paste(img2, anker)

    new_im.save(map_result)


def extend_right(images: [], result: str):
    # first image
    extend_one_right(images[0], images[1], result)

    for img in images[2:]:
        extend_one_right(result, img, result)


def extend_one_down(img1: str, img2: str, res: str, gray=False):
    """extend to images to the right"""
    w1, h1 = get_width_height(img1)
    w2, h2 = get_width_height(img2)
    # print('dimensions of img1 and img2', (w1, h1), (w2, h2) )

    # crop out the template
    wt = w2 // 2
    ht = 50
    x0 = w2 // 4
    y0 = 0
    crop(img2, (x0, y0), (wt, ht), 'tmp/templ.png')

    # template matching
    top_left_found = match(img1, 'tmp/templ.png', img2)

    anker = (top_left_found[0] - x0, top_left_found[1])  # template start not at (0, 0)
    # print('found anker point', anker)

    # stich images
    stitch_down(img1, img2, anker, res, gray)


def extend_down(images: [], result: str):
    # first image
    extend_one_down(images[0], images[1], result)
    for img in images[2:]:
        extend_one_down(result, img, result)


def stitch_all(map_folder, map_matrix, result):
    map_matrix = map_matrix.strip()
    stripes = map_matrix.split('\n')
    stripes = [s for s in stripes if len(s) > 2]
    stripe_images = []

    for i, stripe in enumerate(stripes):
        lstripe = stripe.split(',')
        lstripe = [pathlib.Path(map_folder) / f.strip() for f in lstripe]
        res = pathlib.Path(map_folder) / f'stripe{i}.png'
        stripe_images.append(res)
        extend_right(lstripe, res)

    extend_down(stripe_images, result)


def main():
    map_folder = pathlib.Path('maps/')
    map_matrix = """\
map01.png, map02.png, map03.png
map11.png, map12.png, map13.png
map21.png, map22.png, map23.png\
    """
    layout = [
        [sg.Text('map folder')],
        [sg.Input(map_folder, key='-FOLD-', size=(50,1))],
        [sg.Text('matrix')],
        [sg.Multiline(map_matrix, key='-MAT-', size=(50, 8))],
        [sg.Text('result file')],
        [sg.Input('result.png', key='-RES-', size=(50, 1))],
        [sg.Button('Stitch', key='-RUN-')]
    ]

    win = sg.Window('Stitcher', layout)

    while True:
        event, values = win.read()
        if event is None:
            break
        if event == '-RUN-':
            map_folder = values['-FOLD-']
            map_matrix = values['-MAT-']
            result = values['-RES-']
            stitch_all(map_folder, map_matrix, result)
            sg.popup('\n'.join(g_compare_images), title='Check')


if __name__ == "__main__":
    g_compare_images = []
    main()

