from Degradations import DegradationTrim
from Degradations import DegradationGain
from Degradations import DegradationMp3
from utils import NAME_SEP, PARAMETERS_SEP


class ParametersParser(object):

    available_degradations = [DegradationTrim,
                              DegradationGain,
                              DegradationMp3]

    @staticmethod
    def get_available_degradations_per_name():
        available_degradations_per_name = {}
        for av_degr in ParametersParser.available_degradations:
            available_degradations_per_name[av_degr.name] = av_degr
        return available_degradations_per_name

    @staticmethod
    def parse_degradation_args(degradation_args,
                               available_degradations_per_name):
        print degradation_args
        parameters_values = {}
        name, params_str = degradation_args.split(NAME_SEP)
        degradation = available_degradations_per_name[name]()
        parameters_values_list = params_str.split(PARAMETERS_SEP)
        parameters_info = degradation.parameters_info
        for value, info in zip(parameters_values_list, parameters_info):
            p_name, _, _ = info
            parameters_values[p_name] = value
        degradation.parameters_values = parameters_values
        return degradation

    @staticmethod
    def parse_degradations_args(degradations_args):
        available_degradations_per_name = \
            ParametersParser.get_available_degradations_per_name()
        degradations = []
        for degradation_args in degradations_args:
            degradation = ParametersParser.parse_degradation_args(
                degradation_args, available_degradations_per_name)
            degradations.append(degradation)
        return degradations
