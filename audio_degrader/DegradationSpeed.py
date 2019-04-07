import librosa as lr
import logging
from BaseDegradation import Degradation
from utils import run
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
        cmd = "ffmpeg -y -i {0} -ac 2 -ar {1} -acodec pcm_f32le {2}"
        out, err, returncode = run(cmd.format(
            audio_file.tmp_path,
            int(audio_file.sample_rate / speed_factor),
            extra_tmp_path))
        logging.debug(out)
        logging.debug(err)
        y, sr = lr.core.load(extra_tmp_path, sr=None, mono=False)
        os.remove(extra_tmp_path)
        audio_file.samples = y
