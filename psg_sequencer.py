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

    def is_sig(self):
        return True

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

    def __mul__(self, factor):
        try:
            factor.is_sig()
            a = self.array * factor.array
        except:
            a = self.array * factor
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

        if len(env) > len(self.array):
            env = env[0:len(self.array)]

        if len(env) < len(self.array):
            n = len(self.array) - len(env)
            env = np.append(env, np.zeros(n))

        return Sig(array=env)

    def mul(self, factor):
        factor = self.make_sig(factor)
        a = self.array * factor.array
        return Sig(array=a)


def is_iter(x):
    try:
        _ = (e for e in x)
        return True
    except TypeError:
        return False


def deg2freq(degree):
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


def degs2freqs(degrees):
    # make all iterabel
    degs_iter = []
    for deg in degrees:
        if not is_iter(deg):
            deg = [deg]
        degs_iter.append(deg)

    freqs = []
    for chord in degs_iter:
        chf = [deg2freq(d) for d in chord]
        freqs.append(chf)

    return freqs


def make_chord(instr, freq, dur):
    if not is_iter(freq):
        freq = [freq]

    sig = instr(freq[0], dur)
    for f in freq[1:]:
        sig = sig + instr(f, dur, amp)
    return sig


def instr_default(freq, length):
    atk = 0.01
    sus = length - atk
    rel = 0.01
    le = atk + sus + rel
    env = Sig(le).asr(atk, sus, rel)
    sig1 = Sig(le).rect(freq).mul(env).mul(0.1)
    sig2 = Sig(le).rect(freq * 1.01).mul(env).mul(0.1)
    return sig1


def instr_default(freq, length):
    atk = 0.01
    sus = length - atk
    rel = 0.01
    le = atk + sus + rel
    env = Sig(le).asr(atk, sus, rel)
    sig1 = Sig(le).rect(freq).mul(env).mul(0.1)
    sig2 = Sig(le).rect(freq * 1.01).mul(env).mul(0.1)
    return sig1


def seq(secs, instr=None, abc=None, degrees=None, deltas=1, amps=1, legato=1, stretch=1):
    if abc is not None:
        degrees, deltas = abc2deg(abc, stretch=stretch)

    if instr is None:
        instr = instr_default

    if degrees is None:
        degrees = [41, 43, 45, 50]

    freqs = degs2freqs(degrees)

    if not is_iter(deltas):
        deltas = [deltas] * len(freqs)

    if not is_iter(amps):
        amps = [amps] * len(freqs)

    # calc the length s
    lengths = [d * legato for d in deltas]

    # try find length, needs improvement
    first = make_chord(instr, freqs[0], deltas[0])
    size = secs * first.sr

    a = np.zeros(int(size))
    os = 0
    for freq, delta, amp, length in zip(freqs, deltas, amps, lengths):
        tone = make_chord(instr, freq, length)
        tone = tone * amp
        s = tone.size()
        a[os:s + os] = a[os:s + os] + tone.array[0:s]
        os = os + int(44100 * delta)
    return Sig(array=a)


def abc_dict(abc_note):
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


def abc_trans(abc_dict):
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


def abc2deg(abc, stretch=1):
    pattern = r"\^?[A-G,a-g,z]'*,*\d*/?\d*"
    notes = re.findall(pattern, abc)

    # make list of dicts with keys vorz, pitch, oc, len
    ldict = [abc_dict(note) for note in notes]

    # make list of degree tuples
    ldeg = [abc_trans(dic) for dic in ldict]

    # make a long degree and dur list
    degrees, durs = list(zip(*ldeg))

    durs = [d * stretch for d in durs]

    return degrees, durs


def get_instr_str():
    instr_def = """\
    def my_instrument(freq, length):
        atk = 0.01
        sus = length - atk
        rel = 0.5
        le = atk + sus + rel
        env = Sig(le).asr(atk, sus, rel)
        sig1 = Sig(le).rect(freq).mul(env).mul(0.1)
        sig2 = Sig(le).rect(freq * 1.01).mul(env).mul(0.1)
        res = sig1 + sig2
        return res * 0.5
    """
    return instr_def



def get_abc_str():
    abc = """
        CDEFG2G2 AAAAG4 AAAAG4 FFFFE2E2 GGGGC4
        """
    return abc


if __name__ == '__main__':

    layout = [
        [sg.Multiline('def', key='-INSTR-', size=(70, 20))],
        [sg.Multiline('abd', key='-ABC-', size=(70, 20))],
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
            except:
                sg.popup('Error in  instrument defiinition')
                break
            song = seq(instr=my_instrument, secs=30, abc=abc_str, legato=0.3, stretch=0.5)

            int_array = (song.array * 32767).astype(np.int16)
            wf.write('test.wav', song.sr, int_array)
            winsound.PlaySound('test.wav', winsound.SND_ASYNC)
        elif event == '-STOP-':
            winsound.PlaySound(None, winsound.SND_PURGE)
