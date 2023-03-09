from skip import FrameSkip, TimeSkip
from grayscalemethod import GrayscaleMethod

from typing import Union
import configparser
import re
import os
import math


class Configuration:
    CONFIGURATION_FILE_EXTENSION = '.conf'
    SECTION_NAME = 'slow_movie_player'

    def __init__(self, config_directory: str) -> None:
        self.vcom: float = float('-inf')
        self.screen_width: int = 0
        self.screen_height: int = 0
        self.refresh_timeout: float = 0.0
        self.video_directory: str = ''
        self.skip: Union[FrameSkip, TimeSkip] = FrameSkip(1)

        config_path = self.__get_first_config_file_path_from_directory(config_directory)

        with open(config_path, 'r') as config_file:
            config_string = '[{}]\n{}'.format(
                self.__class__.SECTION_NAME,
                config_file.read()
            )

        parser = configparser.ConfigParser(empty_lines_in_values=False)
        parser.optionxform = lambda option: option
        parser.read_string(config_string)

        self.vcom = parser.getfloat(self.__class__.SECTION_NAME, 'vcom')

        display_resolution_str = self.__strip_enclosing_quotes(
            parser.get(self.__class__.SECTION_NAME, 'display_resolution')
        )

        match = re.fullmatch(r'(\d+)[ \t]*[xX,; \t][ \t]*(\d+)', display_resolution_str)

        if not match:
            raise ValueError("Cannot parse setting for 'display_resolution'.")

        self.screen_width = int(match[1])
        self.screen_height = int(match[2])

        self.refresh_timeout = parser.getfloat(self.__class__.SECTION_NAME, 'refresh_timeout')

        self.video_directory = self.__strip_enclosing_quotes(
            parser.get(self.__class__.SECTION_NAME, 'video_directory')
        )

        frame_skip = parser.getint(self.__class__.SECTION_NAME, 'frame_skip', fallback=None)
        time_skip = parser.getfloat(self.__class__.SECTION_NAME, 'time_skip', fallback=None)

        if time_skip:
            self.skip = TimeSkip(time_skip)
        elif not time_skip and frame_skip:
            self.skip = FrameSkip(frame_skip)

        self.grayscale_method = GrayscaleMethod(
            self.__strip_enclosing_quotes(
                parser.get(self.__class__.SECTION_NAME, 'grayscale_method', fallback='')
            )
        )

        if (math.isinf(self.vcom)
                or self.screen_width <= 0
                or self.screen_height <= 0
                or self.refresh_timeout < 0.0
                or not self.video_directory):
            raise ValueError('Configuration value out of permitted range.')

    @classmethod
    def __get_first_config_file_path_from_directory(cls, config_directory: str) -> str:
        directory_entries = os.scandir(config_directory)

        for entry in directory_entries:
            if entry.is_file() and entry.name.endswith(cls.CONFIGURATION_FILE_EXTENSION):
                return os.path.join(config_directory, entry.name)

        raise FileNotFoundError("No config file found in '{}'.".format(config_directory))

    @staticmethod
    def __strip_enclosing_quotes(string_value: str) -> str:
        quote_marks = ['"', "'"]

        for quote_mark in quote_marks:
            if (len(string_value) > 1
                    and string_value.startswith(quote_mark)
                    and string_value.endswith(quote_mark)):

                return string_value[1:-1]

        return string_value
