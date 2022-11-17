import configparser
import os


class Configuration():
    SECTION_NAME = 'slow_movie_player'

    def __init__(self, config_directory: str) -> None:
        config_path = self.__get_first_config_file_path_from_directory(config_directory)

        with open(config_path, 'r') as config_file:
            config_string = '[{}]\n{}'.format(
                self.__class__.SECTION_NAME,
                config_file.read()
            )

        parser = configparser.ConfigParser()
        parser.optionxform = lambda option: option
        parser.empty_lines_in_values = False
        parser.read_string(config_string)

        self.screen_width = parser.getint(self.__class__.SECTION_NAME, 'screen_width')
        self.screen_height = parser.getint(self.__class__.SECTION_NAME, 'screen_height')
        self.refresh_timeout = parser.getfloat(self.__class__.SECTION_NAME, 'refresh_timeout')
        self.vcom = parser.getfloat(self.__class__.SECTION_NAME, 'vcom')
        self.video_directory = self.__strip_enclosing_quotes(
            parser.get(self.__class__.SECTION_NAME, 'video_directory')
        )

    @staticmethod
    def __get_first_config_file_path_from_directory(config_directory: str) -> str:
        directory_entries = os.scandir(config_directory)

        for entry in directory_entries:
            if entry.is_file() and entry.name.endswith('.conf'):
                return os.path.join(config_directory, entry.name)

        raise FileNotFoundError('No config file found in {}'.format(config_directory))

    @staticmethod
    def __strip_enclosing_quotes(string_value: str) -> str:
        quote_marks = ['"', "'"]

        for quote_mark in quote_marks:
            if (len(string_value) > 1
                and string_value.startswith(quote_mark)
                and string_value.endswith(quote_mark)):

                return string_value[1:-1]

        return string_value
