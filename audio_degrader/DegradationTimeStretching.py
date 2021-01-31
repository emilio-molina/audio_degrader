import soundfile as sf
import logging
import sox
import os
from .BaseDegradation import Degradation


class DegradationTimeStretching(Degradation):

    name = "time_stretch"
    description = "Apply time stretching"
    parameters_info = [
        ("time_stretch_factor",
         "0.9",
         "Time stretch factor")]

    def apply(self, audio_file):
        time_stretch_factor = float(
            self.parameters_values["time_stretch_factor"])
        logging.info(('Time stretching with factor %f' %
                      (time_stretch_factor)))
        extra_tmp_path = audio_file.tmp_path + '.extra.wav'
        tfm = sox.Transformer()
        tfm.tempo(time_stretch_factor)
        tfm.convert(n_channels=2, bitdepth=32)
        tfm.build(audio_file.tmp_path, extra_tmp_path)
        y, sr = sf.read(extra_tmp_path)
        y = y.T
        os.remove(extra_tmp_path)
        audio_file.samples = y
