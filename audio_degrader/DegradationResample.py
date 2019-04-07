from BaseDegradation import Degradation


class DegradationResample(Degradation):

    name = "resample"
    description = "Resample to given sample rate"
    parameters_info = [("sample_rate", "8000", "Desired sample rate [Hz]")]

    def apply(self, degraded_audio_file):
        degraded_audio_file.resample(
            int(self.parameters_values['sample_rate']))
