import numpy as np
import re
import scipy.io.wavfile as wf
import winsound
import PySimpleGUI as sg


class Sig:
    def __init__(self, sec=1.0, const=0.0, array=None):
        self.sr = 44100
        if array is not None:
            self.array = array
        else:
            l = int(self.sr * sec)
            self.array = np.full(l, const)

    def sec(self):
        return len(self.array) / self.sr

    def size(self):
        return len(self.array)

    def make_sig(self, arg):
        # if sig is number, create Sig object"
        try:
            arg.is_sig()
            return arg
        except:
            sec = len(self.array) / self.sr
            return Sig(sec=sec, const=arg)

    def integrate(self):
        a = np.copy(self.array)
        a = a / self.sr
        a = np.cumsum(a)
        return Sig(array=a)

    def __add__(self, sig):
        a = self.array + sig.array
        return Sig(array=a)

    def range(self, min, max):
        x0 = np.min(self.array)
        x1 = np.max(self.array)
        m = (max - min) / (x1 - x0)
        n = min - m * x0
        a = np.copy(self.array)
        a = m * a + n
        return Sig(array=a)

    def sin(self, freq):
        freq = self.make_sig(freq)
        s = freq.integrate().array
        a = np.sin(2 * np.pi * s)
        return Sig(array=a)

    def saw(self, freq):
        freq = self.make_sig(freq)
        s = freq.integrate().array
        a = ((2 * s) % 2) - 1
        return Sig(array=a)

    def rect(self, freq):
        freq = self.make_sig(freq)
        s = freq.integrate().array
        a = np.where(2 * s % 2 > 1, -1, 1)
        return Sig(array=a)

    def tri(self, freq):
        freq = self.make_sig(freq)
        s = freq.integrate().array
        a = np.abs((1 * s - 0.5) % 2 - 1) * 2 - 1
        return Sig(array=a)

    def asr(self, atk, sus, rel):

        # avoid crash when editing instrument
        if atk < 0.0: atk = 0.0
        if sus < 0.0: sus = 0.0
        if rel < 0.0: rel = 0.0
        atk_ar = np.linspace(0, 1, int(self.sr * atk))
        sus_ar = np.linspace(1, 1, int(self.sr * sus))
        rel_ar = np.linspace(1, 0, int(self.sr * rel))

        env = atk_ar
        env = np.append(env, sus_ar)
        env = np.append(env, rel_ar)

        # bring asr to same length
        env = np.resize(env, self.array.shape)

        return Sig(array=env)

    def __mul__(self, factor):
        return self.mul(factor)

    def mul(self, factor):
        try:
            return self.mul_sig(factor)
        except:
            return self.mul_float(factor)

    def mul_float(self, factor):
        factor = float(factor)
        a = self.array * factor
        return Sig(array=a)

    def mul_sig(self, other_sig):
        # bring other to same length
        other_array = np.resize(other_sig.array, self.array.shape)
        a = self.array * other_array
        return Sig(array=a)


class Abc:
    def __init__(self, abc, stretch):

        # split in groups
        # chords seperated by whitespace
        # tones of chords separated by |
        splitted = self.split_abc(abc)

        # bring to list of list structure
        lol_str = self.make_lol_str(splitted)

        # translate to degrees and durations
        degs, deltas = self.make_deg_lol(lol_str)

        # translate degrees to frequencies
        freqs = []
        for chord in degs:
            freq_chord = []
            for deg in chord:
                freq = self.deg2freq(deg)
                freq_chord.append(freq)
            freqs.append(freq_chord)

        deltas = [d * stretch for d in deltas]

        self.abc = abc
        self.freqs = freqs
        self.deltas = deltas

    def make_deg_lol(self, lol_str):
        freqs = []
        deltas = []
        for chord in lol_str:
            deg_chord = []
            for tone in chord:
                dic = self.abc_dict(tone)
                deg, delta = self.abc_trans(dic)
                deg_chord.append(deg)
            freqs.append(deg_chord)
            deltas.append(delta)
        return freqs, deltas

    def make_lol_str(self, splitted):
        """bring splitted abc string to LOL structur """
        lol = []
        for chord in splitted.split(' '):
            lchord = []
            for tone in chord.split('|'):
                lchord.append(tone)
            if tone.strip() != '':
                lol.append(lchord)
        return lol

    def split_abc(self, abc):
        abc = abc.strip()
        pattern = r"\[?_?\^?[A-G,a-g,z],*'*\d?/?\d?\]?"
        l = re.findall(pattern, abc)
        s = ''
        sep = ' '
        for note in l:
            if note.startswith('['):
                sep = '|'
                note = note[1:]
            if note.endswith(']'):
                sep = ' '
                note = note[:-1]
            s = s + note + sep
        return s

    def abc_dict(self, abc_note):
        pattern = r"([_\^]?)([A-G,a-g,z])('*,*)(\d*/?\d*)"

        m = re.match(pattern, abc_note)
        vorz = m.group(1)
        pitch = m.group(2)
        oc = m.group(3)
        le = m.group(4)

        abc_dict = {
            'abc': abc_note,
            'vorz': vorz,
            'pitch': pitch,
            'oc': oc,
            'le': le
        }

        return abc_dict

    def abc_trans(swlf, abc_dict):
        vorz = abc_dict['vorz']  # _ or ^
        pitch = abc_dict['pitch']  # A-G, a-g, z
        oc = abc_dict['oc']  # , '
        le = abc_dict['le']  # empty, or /2, or 3/4

        # Torsten degree definition, minus means half tone done
        dpitch = {
            'z': 0,
            'C': 41, 'D': 42, 'E': 43, 'F': 44, 'G': 45, 'A': 46, 'B': 47,
            'c': 51, 'd': 52, 'e': 53, 'f': 54, 'g': 55, 'a': 56, 'b': 57
        }

        if le == '':
            le = '1'

        if le.startswith('/'):
            le = '1' + le

        dur = eval(le)

        octave = oc.count("'") * 10
        octave = octave - oc.count(",") * 10

        deg = dpitch[pitch] + octave

        if vorz == '_':
            deg = -deg

        if vorz == '^':
            deg = - (deg + 1)

        return (deg, dur)

    def deg2freq(self, degree):
        """convert single degree to frequency"""
        if degree < 0:
            deminish = 1
        else:
            deminish = 0
        degree = abs(degree)
        oc = degree // 10 - 4
        no = degree % 10

        p = 2 ** (1 / 12)

        # make halfton scale
        htones = []
        for n in range(-9, 3):
            f = 440 * p ** n
            htones.append(f)

        # convert degree to halfton nummber
        scale = [0, 0, 2, 4, 5, 7, 9, 11, 13]
        htone_index = scale[no]
        htone_index = htone_index - deminish

        freq = htones[htone_index] * (2 ** oc)
        return round(freq, 2)


class Seq:
    def __init__(self, secs, instr, abc, amps, stretch, legato=1.0):

        abc = Abc(abc, stretch)
        freqs = abc.freqs
        deltas = abc.deltas

        if not self.is_iter(amps):
            amps = [amps] * len(freqs)

        # calc the length s
        lengths = [d * legato for d in deltas]

        # try find length, needs improvement
        first = self.make_chord(instr, freqs[0], deltas[0], amps[0])
        size = secs * first.sr

        a = np.zeros(int(size))
        os = 0

        for freq, delta, amp, length in zip(freqs, deltas, amps, lengths):
            tone = self.make_chord(instr, freq, length, amp)
            tone = tone * amp

            # add tone to result
            s = tone.size()
            a[os:s + os] = a[os:s + os] + tone.array[0:s]
            os = os + int(44100 * delta)
        self.Sig = Sig(array=a)

    @staticmethod
    def is_iter(x):
        try:
            _ = (e for e in x)
            return True
        except TypeError:
            return False

    def make_chord(self, instr, freqs, dur, amp):
        """takes list of frequencies and create sig"""
        if not self.is_iter(freqs):
            freqs = [freqs]

        sig = instr(freqs[0], dur)
        for f in freqs[1:]:
            sig = sig + instr(f, dur) * amp
        return sig


def get_instr_str():
    """define star instrument"""
    instr_def = """\
def my_instrument(freq, length):
    atk = 0.01
    sus = length
    rel = 0.01
    le = atk + sus + rel
    env = Sig(le).asr(atk, sus, rel)
    sig = Sig(le).rect(freq * 0.99)
    return sig * env
    """
    return instr_def


def get_abc_str():
    abc = """\
C/2_E/2G/2[c^dg]
        """
    return abc


if __name__ == '__main__':
    # test a instrument for error solving
    # test = test_instr(440, 1)

    layout = [
        [sg.Multiline('def', key='-INSTR-', size=(70, 20))],
        [sg.Multiline('abd', key='-ABC-', size=(70, 20))],
        [sg.Text('stretch'), sg.Input('1.0', key='-STRETCH-', size=(5,)),
         sg.Text('volume'), sg.Input('0.1', key='-VOL-', size=(5,)),
         sg.Text('legato'), sg.Input('1.0', key='-LEG-', size=(5,)),
         ],
        [sg.Button('run', key='-RUN-'), sg.Button('stop', key='-STOP-')]
    ]

    win = sg.Window('Sequencer', layout, finalize=True)

    instr_str = get_instr_str()
    win['-INSTR-'].update(instr_str)
    abc_str = get_abc_str()
    win['-ABC-'].update(abc_str)

    while True:
        event, values = win.read()
        if event is None:
            break
        elif event == '-RUN-':

            instr_str = values['-INSTR-']
            abc_str = values['-ABC-']


            # def my_instrument(freq, length):
            #     atk = 0.01
            #     sus = length - atk
            #     rel = 0.5
            #     le = atk + sus + rel
            #     env = Sig(le).asr(atk, sus, rel)
            #     sig1 = Sig(le).rect(freq * 0.99)
            #     sig2 = Sig(le).rect(freq * 1.00)
            #     res = sig1 + sig2
            #     return res * env

            try:
                exec(instr_str.strip())
                # test function
                test = my_instrument(440, 1)
            except Exception as e:
                sg.popup('Error in  instrument defiinition', e)
                continue

            stretch = float(values['-STRETCH-'])
            amps = float(values['-VOL-'])
            legato = float(values['-LEG-'])

            # create tho song
            song = Seq(instr=my_instrument, secs=60, abc=abc_str, amps=amps, legato=legato, stretch=stretch).Sig

            int_array = (song.array * 32767).astype(np.int16)
            wf.write('test.wav', song.sr, int_array)
            winsound.PlaySound('test.wav', winsound.SND_ASYNC)

        elif event == '-STOP-':
            winsound.PlaySound(None, winsound.SND_PURGE)

