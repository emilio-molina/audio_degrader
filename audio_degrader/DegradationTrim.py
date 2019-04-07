from BaseDegradation import Degradation


class DegradationTrim(Degradation):

    name = "trim_from"
    description = "Trim audio from a given start time"
    parameters_info = [("start_time", 0.1, "Trim start [seconds]")]

    def apply(self, audio_file):
        start_time = float(self.parameters_values["start_time"])
        start_sample = int(start_time * audio_file.sample_rate)
        audio_file.samples = audio_file.samples[
            :, start_sample:]
