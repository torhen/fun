import PySimpleGUI as sg
from gtts import gTTS
import winsound
from pydub import AudioSegment
import wave
import scipy.io.wavfile as wf
import numpy as np
import pathlib, os
# conda install ffmpeg needed

def prolong_wav(src_wav, dst_wav, seconds):
    # read the src wave
    sr, data = wf.read(src_wav)
    # crate silent array
    sec = len(data) / sr
    to_fill_sec = seconds - sec
    silent_samples = int(to_fill_sec * sr)
    fill_array = np.zeros(silent_samples, dtype=data.dtype)
    wf.write(dst_wav, sr, np.concatenate([data, fill_array]) )


def sentence(text, dst_wav, sec):
    tts = gTTS(text=text, lang='de')
    tts.save("tmp/tmp.mp3")
    sound = AudioSegment.from_mp3("tmp/tmp.mp3")
    sound.export("tmp/tmp.wav", format="wav")
    prolong_wav("tmp/tmp.wav", dst_wav, sec)


def play(wav_file):
    winsound.PlaySound(wav_file, 1)


def cat_wavs(input_files, outfile):
    data = []
    for infile in input_files:
        w = wave.open(infile, 'rb')
        data.append( [w.getparams(), w.readframes(w.getnframes())] )
        w.close()
    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    for i in range(len(input_files)):
        output.writeframes(data[i][1])


def make_result_wav(text):
    ltxt = text.split('\n')
    ltxt = [t.strip() for t in ltxt]
    ltxt = [t for t in ltxt if len(t) > 3] # remove empty lines

    lfiles = []
    for i, txt in enumerate(ltxt):
        sec = float(txt.split()[0])
        txt = ' '.join(txt.split()[1:])
        print(sec, txt)
        file_name = f'tmp/sentence_{str(i).zfill(3)}.wav'
        sentence(txt, file_name, sec)
        lfiles.append(file_name)

    cat_wavs(lfiles, 'result.wav')
    print('result.wav saved.')


def main():
    if not pathlib.Path('tmp').is_dir():
        os.mkdir('tmp')
        print('tmp/ created.')

    layout = [
        [sg.Button('Create WAV', key='-RUN-')],
        [sg.Multiline(key='-TXT-', default_text=default_string, size=(100, 50))]
    ]

    win = sg.Window('voice schedule', layout)

    while True:
        event, values = win.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == '-RUN-':
            make_result_wav(values['-TXT-'])


if __name__ == '__main__':
    default_string = """
    15 Übung begint gleich

    15 Reches Bein zum Po
    15 Noch 15 Sekunden
    15 Rechtes Bein nach hinten
    15 Noch 15 Sekunden
    15 Linkes Bein zum Po
    15 Noch 15 Sekunden
    15 Linkes Bein nach hinten
    15 Noch 15 Sekunden

    15 Reches Bein anwinkeln und Fuss bewegen
    15 Noch 15 Sekunden
    15 Rechtes Bein nach hinten
    15 Noch 15 Sekunden
    15 Linkes Bein anwinkeln und Fuss bewegen
    15 Noch 15 Sekunden
    15 Linkes Bein nach hinten

    15 Noch 15 Sekunden
    15 Reches Bein Spinne
    15 Noch 15 Sekunden
    15 Linkes Bein Spinne
    15 Noch 15 Sekunden

    15 Langsame Kniebeugen
    15 Noch 15 Sekunden
    15 Rumpfbeugen
    15 Noch 15 Sekunden
    15 Kniebeugen
    15 Noch 15 Sekunden
    15 Rumpfbeugen
    15 Noch 15 Sekunden

    15 Rumpfkreisen rechts herum
    15 Rumpfkreisen links herum

    15 Am Türrahmen abstützen und hoch und runter
    15 Noch 15 Sekunden

    15 Armkreisen rechts
    15 Noch 15 Sekunden
    15 Armkreisen links
    15 Noch 15 Sekunden

    15 Rechte Hand an Türrahmen drücken
    15 Noch 15 Sekunden
    15 Linke Hand an Türrahmen drücken
    15 Noch 15 Sekunden

    15 Kopfkreisen rechts herum
    15 Kopfkreisen links herum

    15 Auf alle viere gehen und langsam absitzen
    15 Noch 30 Sekunden
    15 Noch 15 Sekunden
    15 Gewicht nach hinten verlagern
    15 Noch 15 Sekunden

    15 Auf allen vieren Rücken nache oben und unten

    15 Ende der Übung
    """
    main()



