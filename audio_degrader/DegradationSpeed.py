import soundfile as sf
import logging
from .BaseDegradation import Degradation
import sox
import os


class DegradationSpeed(Degradation):

    name = "speed"
    description = "Change playback speed"
    parameters_info = [
        ("speed",
         "0.9",
         "Playback speed factor")]

    def apply(self, audio_file):
        speed_factor = float(self.parameters_values['speed'])
        logging.info('Modifying speed with factor %f' % speed_factor)
        extra_tmp_path = audio_file.tmp_path + '.extra.wav'
        tfm = sox.Transformer()
        tfm.speed(speed_factor)
        tfm.convert(n_channels=2, bitdepth=32)
        tfm.build(audio_file.tmp_path, extra_tmp_path)
        y, sr = sf.read(extra_tmp_path)
        y = y.T
        os.remove(extra_tmp_path)
        audio_file.samples = y
