import numpy
import pyaudio
import math
from lantz import MessageBasedDriver, Feat, ureg
from lantz.core import mfeats
import numpy as np
from lantz import Action

class ToneGenerator(object):

    def __init__(self, samplerate=44100, frames_per_buffer=4410):
        self.p = pyaudio.PyAudio()
        self.samplerate = samplerate
        self.frames_per_buffer = frames_per_buffer
        self.streamOpen = False

    def sinewave(self):
        if self.buffer_offset + self.frames_per_buffer - 1 > self.x_max:
            # We don't need a full buffer or audio so pad the end with 0's
            xs = numpy.arange(self.buffer_offset,
                              self.x_max)
            tmp = self.amplitude * numpy.sin(xs * self.omega)
            out = numpy.append(tmp,
                               numpy.zeros(self.frames_per_buffer - len(tmp)))
        else:
            xs = numpy.arange(self.buffer_offset,
                              self.buffer_offset + self.frames_per_buffer)
            out = self.amplitude * numpy.sin(xs * self.omega)
        self.buffer_offset += self.frames_per_buffer
        return out

    def callback(self, in_data, frame_count, time_info, status):
        if self.buffer_offset < self.x_max:
            data = self.sinewave().astype(numpy.float32)
            return (data.tostring(), pyaudio.paContinue)
        else:
            return (None, pyaudio.paComplete)

    def is_playing(self):
        if self.stream.is_active():
            return True
        else:
            if self.streamOpen:
                self.stream.stop_stream()
                self.stream.close()
                self.streamOpen = False
            return False

    def play(self, frequency, duration, amplitude):
        self.omega = float(frequency) * (math.pi * 2) / self.samplerate
        self.amplitude = amplitude
        self.buffer_offset = 0
        self.streamOpen = True
        self.x_max = math.ceil(self.samplerate * duration) - 1
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=self.samplerate,
                                  output=True,
                                  frames_per_buffer=self.frames_per_buffer,
                                  stream_callback=self.callback)


class Oscilo(MessageBasedDriver):
    MANUFACTURER_ID = '0x0699'
    MODEL_CODE = '0x0363'

    @Feat(read_once=True)
    def i_osciloscopio(self):
        return self.query('*IDN?')

    set_query = MessageBasedDriver.write

    bt_osciloscopio = mfeats.QuantityFeat('HOR:MAIN:SCA?', 'HOR:DEL:SCA {}', units='s', limits=(0.01, 100))

    @Feat(units='Hz')
    def get_frec(self):
        return self.query('MEASU:MEAS{}:VAL?'.format(2))

    @Action()
    def acquire_parameters(self):
        """ Acquire parameters of the osciloscope.
            It is intended for adjusting the values obtained in acquire_curve
        """
        values = 'XZE?;XIN?;PT_OF?;YZE?;YMU?;YOF?;'
        answer = self.query('WFMP:{}'.format(values))
        parameters = {}
        for v, j in zip(values.split('?;'), answer.split(';')):
            parameters[v] = float(j)
        return parameters

    @Action()
    def data_setup(self):
        """ Sets the way data is going to be encoded for sending.
        """
        self.write('DAT:ENC ASCI;WID 1')  # ASCII is the least efficient way, but
        # couldn't make the binary mode to work

    @Action()
    def acquire_curve(self, start=1, stop=2500):
        """ Gets data from the oscilloscope. It accepts setting the start and
            stop points of the acquisition (by default the entire range).
        """
        parameters = self.acquire_parameters()
        self.data_setup()
        self.write('DAT:STAR {}'.format(start))
        self.write('DAT:STOP {}'.format(stop))
        data = self.query('CURV?')
        data = data.split(',')
        data = np.array(list(map(float, data)))
        voltaje = (data - parameters['YOF']) * parameters['YMU']  + parameters['YZE']
        tiempo = np.arange(len(data)) * parameters['XIN'] + parameters['XZE']
        return list(tiempo), list(voltaje)



generator = ToneGenerator()

frequency_start = 1000  # Frequency to start the sweep from
frequency_end = 2000  # Frequency to end the sweep at
num_frequencies = 2  # Number of frequencies in the sweep
amplitude = 1  # Amplitude of the waveform
step_duration = 5  # Time (seconds) to play at each step

for frequency in numpy.logspace(math.log(frequency_start, 10),
                                math.log(frequency_end, 10),
                                num_frequencies):
    print('casiii')
    with Oscilo.via_usb('C102220') as O:
        O.bt_osciloscopio= 5 * (1/frequency) * ureg.seconds #Le pongo una base como para que agarre 5 picos (creo)
        O.set_scale = (amplitude + amplitude/2) * ureg.volt #NECESITO LA FUNCION PARA PONERLE LA ESCALA DE AMPLITUD
    print('casiiii')
    #print("Playing tone at {0:0.2f} Hz".format(frequency))
    generator.play(frequency, step_duration, amplitude)

    m = 0

    while generator.is_playing():
        print("estoy sonando" + str(frequency))

        if m == 0:
            with Oscilo.via_usb('C102220') as O:
                x, y = O.acquire_curve()
                x = np.array(x)
                y = np.array(y)
                data = np.array([x, y])
                data = data.T #estoy bastante segura que tiene que estar
                np.savetxt('timpo' + str(frequency) + '.txt', data, delimiter= " ")
            m=1
        else:
            print("Se tomaron los datos")
