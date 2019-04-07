import librosa as lr
import logging
from utils import run
import os
from BaseDegradation import Degradation


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
        cmd = "rubberband {0} -T {1} --no-threads {2}"
        out, err, returncode = run(cmd.format(
            audio_file.tmp_path,
            time_stretch_factor,
            extra_tmp_path))
        logging.debug(out)
        logging.debug(err)
        y, sr = lr.core.load(extra_tmp_path, sr=None, mono=False)
        os.remove(extra_tmp_path)
        audio_file.samples = y
