import logging
import os
import uuid
import sox
import soundfile as sf


class AudioFile(object):
    """ This class provides all needed methods to interact with an audio file
    """
    def __init__(self, audio_path, tmp_dir='./'):
        basename = os.path.basename(audio_path)
        self.tmp_dir = tmp_dir
        self.applied_degradations = []
        self.audio_path = audio_path
        if not os.path.isdir(tmp_dir):
            os.makedirs(tmp_dir)
        self.tmp_path = os.path.join(tmp_dir,
                                     (basename + '__tmp__' +
                                      str(uuid.uuid4()) + '.wav'))
        self.tmp_path_extra = self.tmp_path + '.extra.wav'
        self._create_tmp_mirror_file()

    def _create_tmp_mirror_file(self):
        tfm = sox.Transformer()
        tfm.convert(n_channels=2, bitdepth=32)
        tfm.build(self.audio_path, self.tmp_path)
        self.samples, self.sample_rate = sf.read(self.tmp_path)
        self.samples = self.samples.T

    def apply_degradation(self, degradation):
        self.applied_degradations.append(degradation)
        logging.debug("Applying {0} degradation".format(degradation))
        degradation.apply(self)
        self._update_mirror_file()

    def _update_mirror_file(self):
        logging.debug("Updating mirror file")
        wav = self.samples
        if wav.ndim > 1 and wav.shape[0] == 2:
            wav = wav.T
        sf.write(self.tmp_path, wav,  self.sample_rate)

    def to_wav(self, output_path):
        tfm = sox.Transformer()
        tfm.convert(n_channels=2, bitdepth=32)
        tfm.build(self.tmp_path, output_path)

    def delete_tmp_files(self):
        logging.debug("Deleting %s" % self.tmp_path)
        os.remove(self.tmp_path)
        if os.path.isfile(self.tmp_path_extra):
            logging.debug("Deleting %s" % self.tmp_path_extra)
            os.remove(self.tmp_path_extra)
        if os.listdir(self.tmp_dir) == []:
            logging.debug("Deleting empty directory %s" % self.tmp_dir)
            os.rmdir(self.tmp_dir)

    def resample(self, new_sample_rate):
        tfm = sox.Transformer()
        tfm.rate(new_sample_rate)
        tfm.convert(n_channels=2, bitdepth=32)
        tfm.build(self.tmp_path, self.tmp_path_extra)

        self.samples, self.sample_rate = sf.read(self.tmp_path_extra)
        self.samples = self.samples.T
        self._update_mirror_file()
