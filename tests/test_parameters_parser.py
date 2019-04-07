from audio_degrader import ParametersParser


class TestParametersParser:

    def test_parameters_parser(self):
        test_str = ["gain,6", "trim_from,3", "normalize"]
        degradations = ParametersParser.parse_degradations_args(test_str)
        assert degradations[0].name == "gain"
        assert degradations[0].parameters_values["value"] == "6"
        assert degradations[1].name == "trim_from"
        assert degradations[1].parameters_values["start_time"] == "3"
        assert degradations[2].name == "normalize"
