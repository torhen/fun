import PySimpleGUI as sg
from bs4 import BeautifulSoup as BS
import requests
import textwrap


class Content:

    def __init__(self):
        self.lines = []
        self.pos = 0
        self.font_size = 12
        self.green = '#00AA00'
        self.red = '#FF0000'
        self.lines_above = 7 # how many lines visible above current

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

    def goto_line(self, nline):
        n = self.get_current_line()
        pos = 0
        for i in range(nline):
            pos = pos + len(self.lines[i]) + 1
        self.pos = pos


    def print_text(self, text_field, cursor_color = None):
        if cursor_color is None:
            cursor_color = self.green
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

        if pressed_key == cursor_letter or pressed_key is None:  # escape
            cursor_color = self.green
            self.change_pos(1)
        else:
            cursor_color = self.red

        self.print_text(text_field, cursor_color)

    def get_current_line(self):
        pos = 0
        for nline, line in enumerate(self.lines):
            pos += len(line)
            if pos >= self.pos:
                return nline

    def get_next_line_start(self):
        pos = 0
        for nline, line in enumerate(self.lines):
            pos += len(line)
            if pos >= self.pos:
                return pos + 1

    def get_perc(self):
        return (self.get_current_line() - self.lines_above) / len(self.lines)


def main():
    line_length = 100
    font_size = 14
    txtfield_size = (100, 30)

    layout = [[sg.Input(key='-URL-', size=(100,),default_text='http://www.spiegel.de'), sg.Button('get', key='-GET-')],
              [sg.Button('down', key='-DOWN-'), sg.Button('up', key='-UP-')],
              [sg.Multiline(size=txtfield_size, key='-TXT-', font=('', font_size), disabled=True,enable_events=True)]
              ]

    win = sg.Window('type trainer', layout, return_keyboard_events=True, use_default_focus=False)

    text_field = win['-TXT-']  # type:sg.Multiline
    test_line = 0
    while True:
        event, values = win.read()
        if event is None:
            break
        elif event == '-GET-':
            url = values['-URL-']
            content = Content()
            content.from_url(url, line_length)
            content.print_text(text_field)

        elif event == 'Escape:27':
            content.key_press(text_field, pressed_key=None)

        elif event == '-DOWN-':
            cur_line = content.get_current_line()
            content.goto_line(cur_line + 1)
            content.print_text(text_field)

        elif event == '-UP-':
            cur_line = content.get_current_line()
            content.goto_line(cur_line - 1)
            content.print_text(text_field)


        elif len(event) == 1:   # key strokes
            pressed_key = event
            content.key_press(text_field, pressed_key=pressed_key)



if __name__ == '__main__':
    main()