import soundfile as sf
import logging
import numpy as np
import sox
import os
from .BaseDegradation import Degradation


class DegradationPitchShifting(Degradation):

    name = "pitch_shift"
    description = "Apply pitch shifting"
    parameters_info = [
        ("pitch_shift_factor",
         "0.9",
         "Pitch shift factor")]

    def apply(self, audio_file):
        pitch_shift_factor = float(
            self.parameters_values["pitch_shift_factor"])
        n_semitones = 12 * np.log2(pitch_shift_factor)
        logging.info('Shifting pitch with factor %f, i.e. %f semitones' %
                     (pitch_shift_factor, n_semitones))
        extra_tmp_path = audio_file.tmp_path + '.extra.wav'
        tfm = sox.Transformer()
        tfm.pitch(n_semitones)
        tfm.convert(n_channels=2, bitdepth=32)
        tfm.build(audio_file.tmp_path, extra_tmp_path)
        y, sr = sf.read(extra_tmp_path)
        y = y.T
        os.remove(extra_tmp_path)
        audio_file.samples = y
