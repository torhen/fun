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
    layout = [[sg.Input(key='-URL-', size=(line_length,),default_text='http://www.spiegel.de'), sg.Button('get', key='-GET-')],
              [sg.Multiline(size=(line_length, 40), key='-TXT-', font=('', 14))]
              ]

    win = sg.Window('type trainer', layout)

    while True:
        event, values = win.read()
        if event is None:
            break
        elif event == '-GET-':
            url = values['-URL-']
            lines = get_text(url, line_length)
            ml = win['-TXT-'] # type:sg.Multiline
            ml.update('')
            for line in lines:
                ml.print(line, text_color='blue')
                ml.print('', text_color='black')


if __name__ == '__main__':
    main()