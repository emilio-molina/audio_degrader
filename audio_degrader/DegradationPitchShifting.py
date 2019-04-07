import librosa as lr
import logging
import numpy as np
from BaseDegradation import Degradation


class DegradationPitchShifting(Degradation):

    name = "pitch_shift"
    description = "Apply pitch shifting"
    parameters_info = [
        ("pitch_shift_factor",
         "0.9",
         "Pitch shift factor")]

    def apply(self, degraded_audio_file):
        x = degraded_audio_file.samples
        sr = degraded_audio_file.sample_rate
        pitch_shift_factor = float(
            self.parameters_values["pitch_shift_factor"])
        n_semitones = 12 * np.log2(pitch_shift_factor)
        logging.info(('Shifting pitch with factor %f, i.e. %f semitones' %
                      (pitch_shift_factor, n_semitones)))
        y0 = lr.effects.pitch_shift(x[0, :], sr, n_semitones,
                                    bins_per_octave=12)
        y1 = lr.effects.pitch_shift(x[1, :], sr, n_semitones,
                                    bins_per_octave=12)
        y = np.zeros((2, len(y0)))
        y[0, :] = y0
        y[1, :] = y1
        degraded_audio_file.samples = y
