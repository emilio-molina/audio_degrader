import os
import librosa as lr
import logging
import uuid
from utils import run


class AudioFile:
    """ This class provides all needed methods to interact with an audio file
    """
    def __init__(self, audio_path, tmp_dir='./'):
        basename = os.path.basename(audio_path)
        self.applied_degradations = []
        self.audio_path = audio_path
        self.tmp_path = os.path.join(tmp_dir,
                                     basename + str(uuid.uuid4()) + '.wav')
        self.x, self.sr = lr.core.load(self.audio_path, sr=None, mono=False)

    def create_tmp_file(self):
        out, err = run("ffmpeg -i {0} -ac 2 -acodec pcm_s16le {1}".format(
            self.audio_path, self.tmp_path))
        logging.debug(out)
        logging.debug(err)

    def apply_degradation(self, degradation):
        self.applied_degradations.append(degradation)

    def delete_tmp_file(self):
        os.remove(self.tmp_path)

    def __del__(self):
        self.delete_tmp_file()
