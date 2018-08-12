import os
import librosa as lr
import logging
import uuid
from utils import run


class DegradedAudioFile(object):
    """ This class provides all needed methods to interact with an audio file
    """
    def __init__(self, audio_path, tmp_dir='./'):
        basename = os.path.basename(audio_path)
        self.applied_degradations = []
        self.audio_path = audio_path
        self.tmp_path = os.path.join(tmp_dir,
                                     basename + str(uuid.uuid4()) + '.wav')
        self.create_tmp_mirror_file()

    def create_tmp_mirror_file(self):
        out, err = run("ffmpeg -y -i {0} -ac 2 -acodec pcm_s32le {1}".format(
            self.audio_path, self.tmp_path))
        self._samples, self.sample_rate = lr.core.load(self.tmp_path,
                                                       sr=None, mono=False)
        logging.debug(out)
        logging.debug(err)

    def apply_degradation(self, degradation):
        self.applied_degradations.append(degradation)
        degradation.apply(self)

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, samples):
        lr.output.write_wav(self.tmp_path, samples,
                            self.sample_rate, norm=False)
        self._samples = samples

    def to_wav(self, output_path):
        out, err = run("ffmpeg -y -i {0} {1}".format(self.tmp_path,
                                                     output_path))
        logging.debug(out)
        logging.debug(err)

    def to_mp3(self, output_path):
        out, err = run("ffmpeg -y -i {0} -b:a 320k {1}".format(self.tmp_path,
                                                               output_path))
        logging.debug(out)
        logging.debug(err)

    def delete_tmp_mirror_file(self):
        os.remove(self.tmp_path)