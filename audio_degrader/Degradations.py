from abc import ABCMeta, abstractmethod


class Degradation(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = "name"
        self.description = "description"
        self.set_parameters_units()
        self.set_parameters_example_values()

    def set_parameters_example_values(self,
            parameters_example_values={'parameter1': 'value1',
                                       'parameter2': 'value2'}):
        self.parameters_example_values = parameters_example_values

    def set_parameters_units(self,
            parameters_units={'parameter1': 'unit1',
                              'parameter2': 'unit2'}):
        self.parameters_units = parameters_units

    def __str__(self):
        return self.name

    def set_parameters_values(self, parameters_values={}):
        self.parameters_values = parameters_values

    @abstractmethod
    def apply(self, audio_file):
        pass


class DegradationTrim(Degradation):

    def __init__(self):
        START_TIME = "start_time"
        self.name = "trim_from"
        self.description = "Trim audio from start"
        self.set_parameters_units({START_TIME, "seconds"})
        self.set_parameters_example_values({START_TIME: 0.1})

    def apply(self, audio_file):
        start_time = self.parameters_values["start_time"]
        start_sample = int(start_time * audio_file.sample_rate)
        audio_file.samples = audio_file.samples[:, start_sample:]


class DegradationMp3(Degradation):

    def apply(self, audio_file):
        pass


class DegradationGain(Degradation):

    def apply(self, audio_file):
        pass


class DegradationNormalization(Degradation):

    def apply(self, audio_file):
        pass


class DegradationMix(Degradation):

    def apply(self, audio_file):
        pass


class DegradationConvolution(Degradation):

    def apply(self, audio_file):
        pass


class DegradationDynamicRangeCompression(Degradation):

    def apply(self, audio_file):
        pass


class DegradationSpeed(Degradation):

    def apply(self, audio_file):
        pass


class DegradationTimeStretching(Degradation):

    def apply(self, audio_file):
        pass


class DegradationPitchShifting(Degradation):

    def apply(self, audio_file):
        pass


class DegradationEqualization(Degradation):

    def apply(self, audio_file):
        pass
