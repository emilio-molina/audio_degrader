from abc import ABCMeta, abstractmethod


class Degradation:
    __metaclass__ = ABCMeta

    def __init__(self, parameters={}):
        self.parameters = parameters

    @abstractmethod
    def apply_degradation(self, audiofile):
        pass


class DegradationTrim(Degradation):

    def apply_degradation(self, audio_file):
        pass


class DegradationMp3(Degradation):

    def apply_degradation(self, audio_file):
        pass


class DegradationGain(Degradation):

    def apply_degradation(self, audio_file):
        pass


class DegradationNormalization(Degradation):

    def apply_degradation(self, audio_file):
        pass


class DegradationMix(Degradation):

    def apply_degradation(self, audio_file):
        pass


class DegradationConvolution(Degradation):

    def apply_degradation(self, audio_file):
        pass


class DegradationDynamicRangeCompression(Degradation):

    def apply_degradation(self, audio_file):
        pass


class DegradationSpeed(Degradation):

    def apply_degradation(self, audio_file):
        pass


class DegradationTimeStretching(Degradation):

    def apply_degradation(self, audio_file):
        pass


class DegradationPitchShifting(Degradation):

    def apply_degradation(self, audio_file):
        pass


class DegradationEqualization(Degradation):

    def apply_degradation(self, audio_file):
        pass
