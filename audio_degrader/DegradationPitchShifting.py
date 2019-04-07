import librosa as lr
import logging
import numpy as np
from utils import run
import os
from BaseDegradation import Degradation


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
        cmd = "rubberband {0} -f {1} --no-threads {2}"
        out, err, returncode = run(cmd.format(
            audio_file.tmp_path,
            pitch_shift_factor,
            extra_tmp_path))
        logging.debug(out)
        logging.debug(err)
        y, sr = lr.core.load(extra_tmp_path, sr=None, mono=False)
        os.remove(extra_tmp_path)
        audio_file.samples = y
