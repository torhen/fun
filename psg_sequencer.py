import numpy as np
import re
import scipy.io.wavfile as wf
import winsound
import time
import PySimpleGUI as sg

class Sig:
    def __init__(self, sec=1, const=0, array=None):
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

    def plot(self, start_sec=0, end_sec=None):
        if end_sec is None:
            end_sec = self.sec()
        n1 = int(self.sr * start_sec)
        n2 = int(self.sr * end_sec)
        a = self.array[n1:n2]
        plt.plot(a)

    def play(self, start_sec=0, end_sec=None):
        if end_sec is None:
            end_sec = self.sec()
        n1 = int(self.sr * start_sec)
        n2 = int(self.sr * end_sec)
        a = self.array[n1:n2]
        return Audio(a, rate=self.sr, autoplay=True, normalize=False)

    def const(self, c):
        sig = Sig(self.sec, const=c)
        return sig

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


class Seq:
    def __init__(self, secs, instr, abc, amps=1, legato=1, stretch=1):

        degrees, deltas = self.abc2deg(abc, stretch=stretch)

        freqs = self.degs2freqs(degrees)

        if not self.is_iter(amps):
            amps = [amps] * len(freqs)

        # calc the length s
        lengths = [d * legato for d in deltas]

        # try find length, needs improvement
        first = self.make_chord(instr, freqs[0], deltas[0])
        size = secs * first.sr

        a = np.zeros(int(size))
        os = 0
        for freq, delta, amp, length in zip(freqs, deltas, amps, lengths):
            tone = self.make_chord(instr, freq, length)
            tone = tone.mul_float(amp)
            s = tone.size()
            a[os:s + os] = a[os:s + os] + tone.array[0:s]
            os = os + int(44100 * delta)
        self.Sig = Sig(array=a)

    def abc_dict(self, abc_note):
        pattern = r"(\^?)([A-G,a-g,z])('*,*)(\d*/?\d*)"
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


    def abc_trans(self, abc_dict):
        vorz = abc_dict['vorz']  # _ or ^
        pitch = abc_dict['pitch']  # A-G, a-g, z
        oc = abc_dict['oc']  # , '
        le = abc_dict['le']  # empty, or /2, or 3/4

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
        return (deg, dur)


    def abc2deg(self, abc, stretch=1):
        pattern = r"\^?[A-G,a-g,z]'*,*\d*/?\d*"
        notes = re.findall(pattern, abc)

        # make list of dicts with keys vorz, pitch, oc, len
        ldict = [self.abc_dict(note) for note in notes]

        # make list of degree tuples
        ldeg = [self.abc_trans(dic) for dic in ldict]

        # make a long degree and dur list
        degrees, durs = list(zip(*ldeg))

        durs = [d * stretch for d in durs]

        return degrees, durs

    def abc_dict(self, abc_note):
        pattern = r"(\^?)([A-G,a-g,z])('*,*)(\d*/?\d*)"
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
        return (deg, dur)

    def degs2freqs(self, degrees):
        # make all iterabel
        degs_iter = []
        for deg in degrees:
            if not self.is_iter(deg):
                deg = [deg]
            degs_iter.append(deg)

        freqs = []
        for chord in degs_iter:
            chf = [self.deg2freq(d) for d in chord]
            freqs.append(chf)

        return freqs

    def is_iter(self, x):
        try:
            _ = (e for e in x)
            return True
        except TypeError:
            return False

    def deg2freq(self, degree):
        "convert single degree to frequency"
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
        return freq

    def make_chord(self, instr, freq, dur):
        if not self.is_iter(freq):
            freq = [freq]

        sig = instr(freq[0], dur)
        for f in freq[1:]:
            sig = sig + instr(f, dur, amp)
        return sig

def get_instr_str():
    """define star instrument"""
    instr_def = """\
def my_instrument(freq, length):
    atk = 0.01
    sus = length - atk
    rel = 0.5
    le = atk + sus + rel
    env = Sig(le).asr(atk, sus, rel)
    sig1 = Sig(le).rect(freq).mul(0.2)
    sig2 = Sig(le).rect(freq * 1.01).mul(0.2)
    res = sig1 + sig2
    return res * env * 0.5
    """
    return instr_def



def get_abc_str():
    abc = """\
CDEFG2G2 AAAAG4 AAAAG4 FFFFE2E2 GGGGC4
        """
    return abc


def test_instr(freq, length):
    atk = 0.01
    sus = length - atk
    rel = 0.5
    le = atk + sus + rel
    env = Sig(le).asr(atk, sus, rel)
    sig1 = Sig(le).rect(freq).mul_sig(env).mul_float(0.1)
    sig2 = Sig(le).rect(freq * 1.01).mul_sig(env).mul_float(0.1)
    res = sig1 + sig2
    return res.mul_float(0.5)


if __name__ == '__main__':
    # test a instrument for error solving
    #test = test_instr(440, 1)

    layout = [
        [sg.Multiline('def', key='-INSTR-', size=(70, 20))],
        [sg.Multiline('abd', key='-ABC-', size=(70, 20))],
        [sg.Text('stretch'), sg.Input('0.5', key='-STRETCH-', size=(8,))],
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
            try:
                exec(instr_str.strip())
                # test function
                test = my_instrument(440, 1)
            except Exception as e:
                sg.popup('Error in  instrument defiinition', e)
                continue

            stretch = float(values['-STRETCH-'])
            song = Seq(instr=my_instrument, secs=60, abc=abc_str, legato=0.3, stretch=stretch).Sig

            int_array = (song.array * 32767).astype(np.int16)
            wf.write('test.wav', song.sr, int_array)
            winsound.PlaySound('test.wav', winsound.SND_ASYNC)
        elif event == '-STOP-':
            winsound.PlaySound(None, winsound.SND_PURGE)
