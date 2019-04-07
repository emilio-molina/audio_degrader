from AllDegradations import ALL_DEGRADATIONS
from utils import NAME_SEP, PARAMETERS_SEP


class ParametersParser(object):
    """ Class able to parse a string defining a degradation"""

    @staticmethod
    def parse_degradation_args(degradation_args):
        """ Parse degradation arguments

        Args:
            degradation_args (string): Input degradation arguments
        Returns:
            (Degradation): Degradation object with specified parameters
        """
        if NAME_SEP in degradation_args:
            return ParametersParser.parse_degradation_args_with_params(
                degradation_args)
        else:
            return ParametersParser.parse_degradation_args_without_params(
                degradation_args)

    @staticmethod
    def parse_degradation_args_with_params(degradation_args):
        """ Parse degradation arguments (with parameters)

        Args:
            degradation_args (string): Input degradation arguments
        Returns:
            (Degradation): Degradation object with specified parameters
        """
        parameters_values = {}
        name = degradation_args.split(NAME_SEP)[0]
        params_str = NAME_SEP.join(degradation_args.split(NAME_SEP)[1:])
        if name not in ALL_DEGRADATIONS:
            raise Exception("Degradation %s not known" % name)
        degradation = ALL_DEGRADATIONS[name]()
        parameters_values_list = params_str.split(PARAMETERS_SEP)
        parameters_info = degradation.parameters_info
        for value, info in zip(parameters_values_list, parameters_info):
            p_name, _, _ = info
            parameters_values[p_name] = value
        degradation.parameters_values = parameters_values
        return degradation

    @staticmethod
    def parse_degradation_args_without_params(degradation_args):
        """ Parse degradation arguments (without parameters)

        Args:
            degradation_args (string): Input degradation arguments
        Returns:
            (Degradation): Degradation object
        """
        name = degradation_args
        if name not in ALL_DEGRADATIONS:
            raise Exception("Degradation %s not known" % name)
        degradation = ALL_DEGRADATIONS[name]()
        return degradation

    @staticmethod
    def parse_degradations_args(degradations_args):
        """ Parse a list of degradations arguments

        Args:
            degradation_args (list of string): Input degradations arguments
        Returns:
            (list of Degradation): Degradation objects with specified params
        """
        degradations = []
        for degradation_args in degradations_args:
            degradation = ParametersParser.parse_degradation_args(
                degradation_args)
            degradations.append(degradation)
        return degradations
