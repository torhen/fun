import PySimpleGUI as sg
from bs4 import BeautifulSoup as BS
import requests
import textwrap


class Content:

    def __intit__(self):
        self.lines = []
        self.pos = 0
        self.font_size = 12

    def get_text(self):
        return '\n'.join(self.lines)

    def from_url(self, url, line_length):
        r = requests.get(url)
        html = r.text
        soup = BS(html, 'html.parser')
        text = soup.text
        text = text.split('\n')
        text = [line for line in text if len(line) > 1]
        text = '\n'.join(text)
        lines = textwrap.wrap(text, line_length, break_long_words=False)
        self.lines = lines
        self.pos = 0


    def change_pos(self, delta):
        new_pos = self.pos + delta
        if new_pos <=0:
            new_pos = 0
        self.pos = new_pos


    def print_text(self, text_field, cursor_color):
        txt_content = self.get_text()
        text_field.update('')
        text_field.print(txt_content[:self.pos], end='', text_color='black')
        text_field.print(txt_content[self.pos], end='', text_color='white', background_color=cursor_color)
        text_field.print(txt_content[self.pos + 1:], end='', text_color='black')
        text_field.set_focus()
        text_field.set_vscroll_position(self.get_perc())


    def key_press(self, text_field, pressed_key):
        txt_content = self.get_text()

        cursor_letter = txt_content[self.pos]

        print(pressed_key, cursor_letter)
        if pressed_key == cursor_letter or pressed_key is None:  # escape
            cursor_color = '#00AA00'
            self.change_pos(1)
        else:
            cursor_color = '#FF0000'

        self.print_text(text_field, cursor_color)

    def get_perc(self):
        return self.pos / len(self.get_text())


def main():
    line_length = 100
    font_size = 14
    txtfield_size = (100, 30)

    layout = [[sg.Input(key='-URL-', size=(100,),default_text='http://www.spiegel.de'), sg.Button('get', key='-GET-')],
              [sg.Multiline(size=txtfield_size, key='-TXT-', font=('', font_size), disabled=True)]
              ]

    win = sg.Window('type trainer', layout, return_keyboard_events=True, use_default_focus=False)

    text_field = win['-TXT-']  # type:sg.Multiline


    while True:
        event, values = win.read()
        if event is None:
            break
        elif event == '-GET-':
            url = values['-URL-']
            content = Content()
            content.from_url(url, line_length)
            content.print_text(text_field, '#00AA00')

        elif event == 'Escape:27':
            content.key_press(text_field, pressed_key=None)

        elif len(event) == 1:   # key strokes
            pressed_key = event
            content.key_press(text_field, pressed_key=pressed_key)


if __name__ == '__main__':
    main()