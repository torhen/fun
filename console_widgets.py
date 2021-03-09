import blessed


class Text:
    def __init__(self, text, location):
        self.text = text
        self.location = location
        self.has_focus = False

    def is_focable(self):
        return False

    def draw(self, term):
        x0, y0 = self.location
        if self.has_focus:
            print(term.move_xy(x0, y0) + term.red(self.text))
        else:
            print(term.move_xy(x0, y0) + self.text)

    def set_focus(self, state):
        self.has_focus = state

    def letter(self, letter):
        pass


class Input:
    def __init__(self, key, location):
        self.text = ''
        self.location = location
        self.key = key
        self.has_focus = False

    def is_focable(self):
        return True

    def draw(self, term):
        x0, y0 = self.location
        if self.has_focus:
            print(term.move_xy(x0, y0) + term.red('[' + self.text + ']'))
        else:
            print(term.move_xy(x0, y0) + '[' + self.text + ']')

    def set_focus(self, state):
        self.has_focus = state

    def letter(self, letter):
        if letter.lower() in "abcdefghijklomnopqrstuvwxyz0123456789.,:' ":
            self.text = self.text + letter
        elif ord(letter) == 127:  # backspace
            self.text = self.text[0:-1]


class Window:
    def __init__(self, title, layout):
        self.title = title

        # separate by focable
        self.elements_focus = []
        self.elements_static = []

        for elem in layout:
            if elem.is_focable():
                self.elements_focus.append(elem)
            else:
                self.elements_static.append(elem)

        self.has_focus = 0
        self.term = blessed.Terminal()
        self.elements_focus[self.has_focus ].set_focus(True)
        self.draw()

    def draw(self):
        print(self.term.clear + self.term.home)

        # draw static elements
        for elem in self.elements_static:
            elem.draw(self.term)

        # draw focable elements
        for elem in self.elements_focus:
            elem.draw(self.term)

    def read(self):
        val = self.term.inkey()
        self.letter(val)
        return val, 0

    def letter(self, letter):
        self.elements_focus[self.has_focus].letter(letter)

    def next_focus(self):
        # delete focus of the current
        self.elements_focus[self.has_focus].set_focus(False)
        # increase focus
        self.has_focus += 1

        # if to high, set to zero
        if self.has_focus >= len(self.elements_focus):
            self.has_focus = 0
        self.elements_focus[self.has_focus ].set_focus(True)

layout = [
        Text('CONVERT SWISS -> WGS84', location=(1, 1)),
        Text('coord x:', location=(1, 3)), Input(key='-X-', location=(12, 3)),
        Text('coord y:', location=(1, 4)), Input(key='-Y-', location=(12, 4)),
        ]

win = Window('test', layout)

with win.term.cbreak(), win.term.hidden_cursor():
    while True:
        event, values = win.read()
        if event == 'q':
            print('app finishes.')
            break
        elif ord(event) == 9:
            print('capslock')
            win.next_focus()
        win.draw()
        print(ord(event))

