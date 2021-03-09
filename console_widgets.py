import blessed


class Text:
    def __init__(self, text, location):
        self.text = text
        self.location = location
        self.has_focus = False

    def get_key(self):
        return self.key

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
    def __init__(self, key, location, default_value=''):
        self.text = default_value
        self.location = location
        self.key = key
        self.has_focus = False

    def get_key(self):
        return self.key

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

    def update(self, text):
        self.text = text

    def get_value(self):
        return self.text


class Button:
    def __init__(self, text, key, location):
        self.text = text
        self.location = location
        self.key = key
        self.has_focus = False

    def get_key(self):
        return self.key

    def is_focable(self):
        return True

    def draw(self, term):
        x0, y0 = self.location
        if self.has_focus:
            print(term.move_xy(x0, y0) + term.red('<' + self.text + '>'))
        else:
            print(term.move_xy(x0, y0) + '<' + self.text + '>')

    def set_focus(self, state):
        self.has_focus = state

    def letter(self, letter):
        if letter == 13:
            print('Button' + self.text + ' pressed.')

    def get_value(self):
        return ''


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

        focus_key = self.elements_focus[self.has_focus].get_key()

        if ord(val) == 9:  # capslock
            win.next_focus()

        elif ord(val) == 13:  # return
            val = focus_key

        values = {}
        for elem in self.elements_focus:
            values[elem.get_key()] = elem.get_value()

        return val, values

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

    def get_element(self, key):
        for elem in self.elements_focus:
            if elem.get_key() == key:
                return elem


layout = [
        Text('CONVERT SWISS -> WGS84', location=(1, 1)),
        Text('coord x:', location=(1, 3)), Input(key='-X-', location=(12, 3), default_value='600000'),
        Text('coord y:', location=(1, 4)), Input(key='-Y-', location=(12, 4), default_value='200000'),
        Button('Calc', key='-CALC-', location=(1, 6)),
        Button('Clear', key='-CLEAR-', location=(9, 6)),
        Input(key='-RES-', location=(1, 9)),
        ]

win = Window('test', layout)

with win.term.cbreak(), win.term.hidden_cursor():
    while True:
        event, values = win.read()
        if event == 'q':
            print('app finishes.')
            break

        if event == '-CALC-':
            x = float(values['-X-'])
            y = float(values['-Y-'])
            res = x + y
            win.get_element('-RES-').update(str(res))

        if event == '-CLEAR-':
            win.get_element('-X-').update('0')
            win.get_element('-Y-').update('0')

        win.draw()
        print(event, values)