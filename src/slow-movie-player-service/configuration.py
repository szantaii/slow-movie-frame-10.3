import configparser
import os
from typing import Union


class Configuration():
    PARSER_DUMMY_SECTION = 'slow_movie_player'
    REQUIRED_ENTRY_AND_TYPE_PAIRS = (
        ('display_horizontal_resolution', 'int'),
        ('display_vertical_resolution',   'int'),
        ('refresh_timeout',               'float'),
        ('vcom',                          'str'),
        ('video_directory',               'str'),
    )

    def __init__(self, config_directory: str) -> None:
        config_path = self.__get_first_config_file_path_from_directory(config_directory)

        with open(config_path, 'r') as config_file:
            config_string = '[{}]\n{}'.format(
                self.__class__.PARSER_DUMMY_SECTION,
                config_file.read()
            )

        parser = configparser.ConfigParser()
        parser.optionxform = lambda option: option
        parser.empty_lines_in_values = False
        parser.read_string(config_string)

        for attr_name, attr_type in self.__class__.REQUIRED_ENTRY_AND_TYPE_PAIRS:
            setattr(
                self,
                attr_name,
                self.__convert(
                    attr_type,
                    parser.get(self.__class__.PARSER_DUMMY_SECTION, attr_name)
                )
            )

    def __convert(self, data_type: str, value: str) -> Union[float, int, str]:
        if data_type == 'float':
            return float(value)

        if data_type == 'int':
            return abs(int(value))

        if data_type == 'str':
            quotes = ['"', "'"]

            for quote in quotes:
                if value.startswith(quote) and value.endswith(quote):
                    return value.strip(quote)

            return value

        raise ValueError("data_type must have a value of 'float', 'int' or 'str'.")

    @staticmethod
    def __get_first_config_file_path_from_directory(config_directory: str) -> str:
        directory_entries = os.scandir(config_directory)

        for entry in directory_entries:
            if entry.is_file() and entry.name.endswith('.conf'):
                return os.path.join(config_directory, entry.name)

        raise FileNotFoundError('No config file found in {}'.format(config_directory))
