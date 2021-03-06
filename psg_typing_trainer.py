import PySimpleGUI as sg
from bs4 import BeautifulSoup as BS
import requests
import textwrap


class Content:

    def __init__(self, graph, canvas_size):
        self.graph = graph # type:sg.graph
        self.lines = []
        self.font = ('Courier', 14)
        self.line_spacing = 33
        self.char_spacing = 11
        self.canvas_size = canvas_size
        self.green = "#00AA00"
        self.red = '#FF0000'
        self.cursor_line = 0
        self.cursor_char = 0
        self.line_length = canvas_size[0] // self.char_spacing - 1
        self.all_lines = []
        self.first_displayed_line = 0
        self.visible_lines_above = 5

    def from_url(self, url):
        r = requests.get(url)
        html = r.text
        soup = BS(html, 'html.parser')
        text = soup.text
        text = text.split('\n')
        text = [line for line in text if len(line) > 1]
        text = '\n'.join(text)
        lines = textwrap.wrap(text, self.line_length, break_long_words=True)
        self.all_lines = lines
        self.lines = self.all_lines
        self.pos = 0
        self.graph.set_focus()

    def print_text(self):
        pos = 0
        self.graph.erase()
        lines = self.lines[:]
        for i, line in enumerate(lines):
            self.graph.draw_text(line, location=(0, pos),
                    text_location=sg.TEXT_LOCATION_TOP_LEFT,
                    font = self.font)

            pos = pos + self.line_spacing

        # Cursor
        top_left = (self.cursor_char * self.char_spacing, self.line_spacing)
        bottom_right = (self.char_spacing, self.line_spacing)

        self.cursor_obj_red = self.graph.draw_rectangle(
                                top_left=top_left,
                                bottom_right=bottom_right,
                                line_color=self.red,
                                line_width=5)

        self.cursor_obj_green = self.graph.draw_rectangle(
                                top_left=top_left,
                                bottom_right=bottom_right,
                                line_color=self.green,
                                line_width=5)

        self.set_cursor(0, 0)

    def get_cursor(self):
        return self.cursor_char, self.cursor_line

    def set_cursor(self, char, line):

        if char <= 0:
            char = 0

        if char >= len(self.lines[line]):
            char = len(self.lines[line])

        self.cursor_char = char
        self.cursor_line = line
        curs_x = self.cursor_char * self.char_spacing
        curs_y = self.cursor_line * self.line_spacing + self.line_spacing
        self.graph.relocate_figure(self.cursor_obj_green, curs_x, curs_y)
        self.graph.relocate_figure(self.cursor_obj_red, curs_x, curs_y)
        self.set_cur_color('green')

    def set_cur_color(self, color):
        if color == 'red':
            self.graph.send_figure_to_back(self.cursor_obj_green)
        else:
            self.graph.send_figure_to_back(self.cursor_obj_red)

    def move_cursor(self, dx, dy):
        cur_x, cur_y = self.get_cursor()
        self.set_cursor(cur_x + dx, cur_y + dy)
        self.set_cur_color('green')


    def get_cursor_letter(self):
        line = self.cursor_line
        char = self.cursor_char
        if line < 0 or line >= len(self.lines):
            return '§'
        if char <0 or char >= len(self.lines[line]):
            return '§'
        return self.lines[line][char]

    def key_press(self, pressed_key):
        cursor_letter = self.get_cursor_letter()
        # print(pressed_key, cursor_letter)
        if pressed_key == cursor_letter:
            self.move_cursor(1, 0)
        else:
            self.set_cur_color('red')

    def find_cursor(self):
        visible_lines = self.visible_lines_above
        x, y = self.get_cursor()
        shift = y - visible_lines

        if self.first_displayed_line + shift < 0:
            return
        if self.first_displayed_line + shift >= len(self.all_lines):
            return

        self.first_displayed_line = self.first_displayed_line + shift
        self.lines = self.all_lines[self.first_displayed_line:]
        self.print_text()
        x, y = self.get_cursor()
        self.set_cursor(x, visible_lines)

    def up_down(self, nlines):
        x, y = self.get_cursor()
        self.set_cursor(0, y)
        self.first_displayed_line += nlines

        if self.first_displayed_line < 0:
            self.first_displayed_line = 0
            return

        if self.first_displayed_line >= len(self.all_lines):
            self.first_displayed_line == len(self.all_lines)

        self.lines = self.all_lines[self.first_displayed_line:]
        self.print_text()
        self.set_cursor(x, y - nlines)


def main():
    canvas_size = (800, 500)

    layout = [[sg.Input(key='-URL-', size=(100,),default_text='http://www.spiegel.de'), sg.Button('get', key='-GET-')],

                [sg.Button('page down', key='-PGDN-'), sg.Button('page up', key='-PGUP-')],
              [sg.Graph(canvas_size=canvas_size, key='-TXT-',
                        graph_bottom_left=(0, canvas_size[0]), graph_top_right=(canvas_size[0], 0),
                        background_color='white',
                        enable_events=True)]
              ]

    win = sg.Window('type trainer', layout, return_keyboard_events=True, use_default_focus=False)

    graph = win['-TXT-']  # type:Graph
    content = Content(graph, canvas_size=canvas_size)

    while True:
        event, values = win.read()

        if event is None:
            break
        elif event == '-GET-':
            url = values['-URL-']
            content.from_url(url)
            content.print_text()

        elif ord(event[0]) == 13:  # return
            x, y = content.get_cursor()
            content.set_cursor(0, y + 1)
            content.find_cursor()

        elif event == 'Escape:27':
            print('escape')

        elif event == 'Right:39':
            content.move_cursor(1, 0)

        elif event == 'Left:37':
            content.move_cursor(-1, 0)

        elif event == 'Down:40':
            content.move_cursor(0, 1)
            content.find_cursor()

        elif event == 'Up:38':
            content.move_cursor(0, -1)
            content.find_cursor()

        elif len(event) == 1:   # key strokes
            pressed_key = event
            content.key_press(pressed_key)

        elif event == '-PGDN-':
            content.up_down(10)
            content.move_cursor(0, 10)

        elif event == '-PGUP-':
            content.up_down(-10)
            content.move_cursor(0, -10)

        else:
            pass
            #print(event)


if __name__ == '__main__':
    main()