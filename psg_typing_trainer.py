import PySimpleGUI as sg
from bs4 import BeautifulSoup as BS
import requests
import textwrap


def get_text(url, line_length):
    r = requests.get(url)
    html = r.text
    soup = BS(html, 'html.parser')
    text = soup.text
    text = text.split('\n')
    text = [line for line in text if len(line)>1]
    text = '\n'.join(text)
    text = textwrap.wrap(text, line_length, break_long_words=False)
    return text


def main():
    line_length = 100
    font_size = 14
    txtfield_size = (100, 30)

    layout = [[sg.Input(key='-URL-', size=(100,),default_text='http://www.spiegel.de'), sg.Button('get', key='-GET-')],
              [sg.Multiline(size=txtfield_size, key='-TXT-', font=('', font_size), disabled=True)]
              ]

    win = sg.Window('type trainer', layout, return_keyboard_events=True, use_default_focus=False)

    txt_field = win['-TXT-']  # type:sg.Multiline
    txt_content = ''

    while True:
        event, values = win.read()
        if event is None:
            break
        elif event == '-GET-':
            url = values['-URL-']
            lines = get_text(url, line_length)
            txt_content = '\n'.join(lines)
            txt_pos = 0
            pressed_key = None
            update_text(txt_field, txt_content, txt_pos, font_size=font_size, pressed_key=pressed_key)
        elif len(event) == 1:   # key strokes
            pressed_key = event
            if txt_pos < len(txt_content) - 1:
                txt_pos += 1
            res = update_text(txt_field, txt_content, txt_pos, font_size=font_size, pressed_key=pressed_key)
            if res == False:
                txt_pos = txt_pos - 1
                update_text(txt_field, txt_content, txt_pos, font_size=font_size, pressed_key=pressed_key)


def update_text(txt_field, txt_content, txt_pos, font_size, pressed_key):
    print(pressed_key, txt_content[txt_pos-1])
    if pressed_key == txt_content[txt_pos-1] or pressed_key is None or pressed_key == '§':  # escape
        cursor_color = '#00AA00'
        ret = True
    else:
        cursor_color = '#FF0000'
        ret = False

    txt_field.update('')
    txt_field.print(txt_content[:txt_pos], end='', text_color='black')
    txt_field.print(txt_content[txt_pos], end='', text_color='white', background_color=cursor_color)
    txt_field.print(txt_content[txt_pos+1:], end='', text_color='black')
    txt_field.set_focus()
    txt_field.set_vscroll_position(0)

    return ret


if __name__ == '__main__':
    main()