import librosa as lr
import logging
import numpy as np
from BaseDegradation import Degradation


class DegradationTimeStretching(Degradation):

    name = "time_stretch"
    description = "Apply time stretching"
    parameters_info = [
        ("time_stretch_factor",
         "0.9",
         "Time stretch factor")]

    def apply(self, degraded_audio_file):
        x = degraded_audio_file.samples
        time_stretch_factor = float(
            self.parameters_values["time_stretch_factor"])
        logging.info(('Time stretching with factor %f' %
                      (time_stretch_factor)))
        y0 = lr.effects.time_stretch(x[0, :], time_stretch_factor)
        y1 = lr.effects.time_stretch(x[1, :], time_stretch_factor)
        y = np.zeros((2, len(y0)))
        y[0, :] = y0
        y[1, :] = y1
        degraded_audio_file.samples = y
