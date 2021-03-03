import PySimpleGUI as sg
from bs4 import BeautifulSoup as BS
import requests
import textwrap


class Content:

    def __init__(self, canvas_size):
        self.lines = []
        self.pos = 0
        self.font = ('Courier', 14)
        self.line_spacing = 30
        self.char_spacing = 11
        self.canvas_size = canvas_size
        self.show_lines = int(1.5 * canvas_size[1] / self.line_spacing)
        self.green = "#00AA00"
        self.cursor_pos = 0

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

    def print_text(self, text_field:sg.Graph, line_nmb):
        pos = 0
        text_field.draw_rectangle(top_left=(0, 0), bottom_right=(30, 30), fill_color=self.green)
        lines = self.lines[line_nmb: line_nmb + self.show_lines]
        text_field.erase()
        for i, line in enumerate(lines):
            text_field.draw_text(line, location=(0, pos),
                    text_location=sg.TEXT_LOCATION_TOP_LEFT, font = self.font)
            pos = pos + self.line_spacing

        self.cursor_obj = text_field.draw_rectangle(top_left=(self.cursor_pos, 30),
                                  bottom_right=(self.cursor_pos + self.char_spacing, 30),
                                  line_color=self.green, line_width=5)

    def key_press(self, text_field, pressed_key):
        print(pressed_key)
        self.cursor_pos += 1
        text_field.relocate_figure(self.cursor_obj, self.cursor_pos * self.char_spacing, 30)

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
    line_length = 70
    font_size = 14
    canvas_size = (800, 500)

    layout = [[sg.Input(key='-URL-', size=(100,),default_text='http://www.spiegel.de'), sg.Button('get', key='-GET-')],
              [sg.Graph(canvas_size=canvas_size, key='-TXT-',
                        graph_bottom_left=(0, canvas_size[0]), graph_top_right=(canvas_size[0], 0),
                        background_color='white',
                        enable_events=True)]
              ]

    win = sg.Window('type trainer', layout, return_keyboard_events=True, use_default_focus=False)

    text_field = win['-TXT-']  # type:Graph
    line_nmb = 0
    while True:
        event, values = win.read()
        if event is None:
            break
        elif event == '-GET-':
            url = values['-URL-']
            content = Content(canvas_size=canvas_size)
            content.from_url(url, line_length)
            content.print_text(text_field, line_nmb=line_nmb)

        elif event == 'Escape:27':
            content.key_press(text_field, pressed_key=None)

        elif event == 'Down:40':
            line_nmb += 1
            content.print_text(text_field, line_nmb=line_nmb)

        elif event == 'Up:38':
            line_nmb -= 1
            content.print_text(text_field, line_nmb=line_nmb)


        elif len(event) == 1:   # key strokes
            pressed_key = event
            content.key_press(text_field, pressed_key=pressed_key)

        else:
            print(event)



if __name__ == '__main__':
    main()