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
            #txt_content = "Das ist ein Test\nein weiterer Test"
            txt_pos = 0
            update_text(txt_field, txt_content, txt_pos, font_size=font_size)
        elif len(event) == 1:   # key strokes
            print(event)
            if txt_pos < len(txt_content) - 1:
                txt_pos += 1
            update_text(txt_field, txt_content, txt_pos, font_size=font_size)


def update_text(txt_field, txt_content, txt_pos, font_size):
    txt_field.update('')
    txt_field.print(txt_content[:txt_pos], end='', text_color='black')
    txt_field.print(txt_content[txt_pos], end='', text_color='white', background_color='#00AA00')
    txt_field.print(txt_content[txt_pos+1:], end='', text_color='black')
    txt_field.set_focus()
    txt_field.set_vscroll_position(0)


if __name__ == '__main__':
    main()