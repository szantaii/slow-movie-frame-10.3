from module_helper import get_module_from_file
from unittest import TestCase
import configparser
import tempfile
import os
import sys
from typing import Any

skip = get_module_from_file('../../src/slow-movie-player-service/skip.py')
grayscalemethod = get_module_from_file('../../src/slow-movie-player-service/grayscalemethod.py')
configuration = get_module_from_file('../../src/slow-movie-player-service/configuration.py')


class ConfigurationTest(TestCase):
    def setUp(self) -> None:
        super().setUp()

        config_directory = tempfile.mkdtemp()
        config_file = tempfile.NamedTemporaryFile(
            dir=config_directory,
            suffix=configuration.Configuration.CONFIGURATION_FILE_EXTENSION,
            delete=False
        )

        config_file.close()

        self.config_file_path = config_file.name
        self.config_directory_path = config_directory

    def tearDown(self) -> None:
        os.remove(self.config_file_path)
        os.rmdir(self.config_directory_path)

        super().tearDown()

    def test_configuration_with_valid_configurations(self) -> None:
        cases: list[dict[str, Any]] = [
            {
                'description': 'Minimal valid config',
                'config_file_contents': (
                    'video_directory = "/"\n'
                    'vcom = -1\n'
                    "display_resolution = '1x2'\n"
                    'refresh_timeout = 1\n'
                ),
                'config_attribute_name_expected_value_pairs': {
                    'vcom': -1.0,
                    'screen_width': 1,
                    'screen_height': 2,
                    'refresh_timeout': 1.0,
                    'video_directory': '/',
                    'skip': skip.FrameSkip(1),
                    'grayscale_method': grayscalemethod.GrayscaleMethod(''),
                },
            },
            {
                'description': 'Valid config with no spaces surrounding assignment characters',
                'config_file_contents': (
                    'vcom=-123456.789\n'
                    "display_resolution=1024x768\n"
                    'refresh_timeout=987.654321\n'
                    'video_directory=/ path / with \t/\twhitespace characters\n'
                    'frame_skip=97\n'
                    'grayscale_method=Average'
                ),
                'config_attribute_name_expected_value_pairs': {
                    'vcom': -123456.789,
                    'screen_width': 1024,
                    'screen_height': 768,
                    'refresh_timeout': 987.654321,
                    'video_directory': '/ path / with \t/\twhitespace characters',
                    'skip': skip.FrameSkip(97),
                    'grayscale_method': grayscalemethod.GrayscaleMethod('Average'),
                },
            },
            {
                'description': 'Valid config with exaggerated values',
                'config_file_contents': (
                    'vcom = {vcom}\n'
                    'display_resolution = {screen_width} X {screen_height}\n'
                    'refresh_timeout = {refresh_timeout}\n'
                    'video_directory = {video_directory}\n'
                    'time_skip = {time_skip}\n'
                    'frame_skip = {frame_skip}\n'
                    "grayscale_method = 'Rec601Luminance'\n"
                ).format(
                    vcom='-0.{}'.format('1' * sys.float_info.dig),
                    screen_width=str(int(sys.float_info.max) // 2 - 1),
                    screen_height=str(int(sys.float_info.max) // 2 + 1),
                    refresh_timeout='{}.1'.format('9' * sys.float_info.dig),
                    video_directory='/directory' * 10,
                    time_skip='{0}.{0}'.format('5' * (sys.float_info.dig // 2)),
                    frame_skip=str(int(sys.float_info.max)),
                ),
                'config_attribute_name_expected_value_pairs': {
                    'vcom': float('-0.{}'.format('1' * sys.float_info.dig)),
                    'screen_width': int(sys.float_info.max) // 2 - 1,
                    'screen_height': int(sys.float_info.max) // 2 + 1,
                    'refresh_timeout': float('{}.1'.format('9' * sys.float_info.dig)),
                    'video_directory': '/directory' * 10,
                    'skip': skip.TimeSkip(float('{0}.{0}'.format('5' * (sys.float_info.dig // 2)))),
                    'grayscale_method': grayscalemethod.GrayscaleMethod('Rec601Luminance'),
                },
            },
            {
                'description': 'Valid configuration with misspelled grayscale_method value',
                'config_file_contents': (
                    'vcom = 123\n'
                    'display_resolution = 456\t\t789\n'
                    'refresh_timeout = 987\n'
                    'video_directory = /path/to/video/directory\n'
                    'frame_skip = 654\n'
                    'time_skip = 321\n'
                    'grayscale_method = "there is a typo in_this value but it does not matter"\n'
                ),
                'config_attribute_name_expected_value_pairs': {
                    'vcom': 123.0,
                    'screen_width': 456,
                    'screen_height': 789,
                    'refresh_timeout': 987.0,
                    'video_directory': '/path/to/video/directory',
                    'skip': skip.TimeSkip(321.0),
                    'grayscale_method': grayscalemethod.GrayscaleMethod('the default will be used here anyway'),
                },
            },
            {
                'description': 'Valid configuration with another format for display_resolution',
                'config_file_contents': (
                    'vcom = -111.111\n'
                    'display_resolution = 222 333\n'
                    'refresh_timeout = 444.444\n'
                    'video_directory = /another video directory path\n'
                    'frame_skip = 555\n'
                    'time_skip = 666.666\n'
                    'grayscale_method = RMS\n'
                ),
                'config_attribute_name_expected_value_pairs': {
                    'vcom': -111.111,
                    'screen_width': 222,
                    'screen_height': 333,
                    'refresh_timeout': 444.444,
                    'video_directory': '/another video directory path',
                    'skip': skip.TimeSkip(666.666),
                    'grayscale_method': grayscalemethod.GrayscaleMethod('RMS'),
                },
            },
            {
                'description': 'Valid config with unicode characters in video_directory path',
                'config_file_contents': (
                    'vcom = -987.654\n'
                    'display_resolution = 1080;2400\n'
                    'refresh_timeout = 1\n'
                    'video_directory = \u00AF\u005C\u005F\u0028\u30C4\u0029\u005F\u002F\u00AF\n'
                    'frame_skip = 555\n'
                    'grayscale_method = RMS\n'
                ),
                'config_attribute_name_expected_value_pairs': {
                    'vcom': -987.654,
                    'screen_width': 1080,
                    'screen_height': 2400,
                    'refresh_timeout': 1.0,
                    'video_directory': r"¯\_(ツ)_/¯",
                    'skip': skip.FrameSkip(555),
                    'grayscale_method': grayscalemethod.GrayscaleMethod('RMS'),
                },
            },
            {
                'description': 'Valid config with yet another format for display_resolution',
                'config_file_contents': (
                    'vcom = 767.787\n'
                    'display_resolution = "878 ,898"\n'
                    'refresh_timeout = 121.212\n'
                    'video_directory = /this/is/the/last/one\n'
                    'time_skip = 232.323\n'
                    'frame_skip = 434\n'
                    'grayscale_method = Brightness\n'
                ),
                'config_attribute_name_expected_value_pairs': {
                    'vcom': 767.787,
                    'screen_width': 878,
                    'screen_height': 898,
                    'refresh_timeout': 121.212,
                    'video_directory': '/this/is/the/last/one',
                    'skip': skip.TimeSkip(232.323),
                    'grayscale_method': grayscalemethod.GrayscaleMethod('Brightness'),
                },
            },
        ]

        for case in cases:
            with self.subTest(case['description']):
                with open(self.config_file_path, mode='w') as config_file:
                    config_file.write(case['config_file_contents'])

                config = configuration.Configuration(self.config_directory_path)

                for attribute_name, expected_value in case['config_attribute_name_expected_value_pairs'].items():
                    self.assertEqual(
                        getattr(config, attribute_name),
                        expected_value
                    )

    def test_configuration_with_missing_mandatory_options(self) -> None:
        cases: list[dict[str, str]] = [
            {
                'config_file_contents': '',
                'missing_mandatory_option': 'vcom',
            },
            {
                'config_file_contents': 'vcom = 0.001',
                'missing_mandatory_option': 'display_resolution',
            },
            {
                'config_file_contents': (
                    'vcom = 0.001\n'
                    'display_resolution = 2x3'
                ),
                'missing_mandatory_option': 'refresh_timeout',
            },
            {
                'config_file_contents': (
                    'vcom = -0.999\n'
                    'display_resolution = 1024, 768\n'
                    'refresh_timeout = 0.001'
                ),
                'missing_mandatory_option': 'video_directory',
            },
        ]

        for case in cases:
            with self.subTest(missing_mandatory_option=case['missing_mandatory_option']):
                with open(self.config_file_path, mode='w') as config_file:
                    config_file.write(case['config_file_contents'])

                self.assertRaisesRegex(
                    configparser.NoOptionError,
                    r"^No option '{}' in section: '{}'$".format(
                        case['missing_mandatory_option'],
                        configuration.Configuration.SECTION_NAME
                    ),
                    configuration.Configuration,
                    self.config_directory_path
                )

    def test_configuration_with_malformed_display_resolution_strings(self) -> None:
        config_file_contents_template = (
            'vcom = -1.48\n'
            'display_resolution = {}\n'
            'refresh_timeout = 300.0\n'
            'video_directory = /just/another/valid/path/to/video/directory\n'
            'time_skip = 100.0\n'
            'frame_skip = 3\n'
            'grayscale_method = Rec709Luma\n'
        )

        cases: list[dict[str, str]] = [
            {
                'description': 'Empty string for display_resolution #1',
                'display_resolution': '',
            },
            {
                'description': 'Empty string for display_resolution #2',
                'display_resolution': '""',
            },
            {
                'description': 'Empty string for display_resolution #3',
                'display_resolution': "''",
            },
            {
                'description': 'Single number for display_resolution',
                'display_resolution': '1872',
            },
            {
                'description': 'Floating point number in display_resolution',
                'display_resolution': '1024 x 768.0',
            },
            {
                'description': 'Unicode multiplication sign as separator in display_resolution',
                'display_resolution': '1920×1080',
            },
            {
                'description': 'Vertical tab as whitespace in display_resolution',
                'display_resolution': '640\v480',
            },
            {
                'description': 'Form feed character as whitespace in display_resolution',
                'display_resolution': '3840\f2160',
            },
            {
                'description': 'Non-breaking space as whitespace in display_resolution',
                'display_resolution': '1080\u00A02400',
            },
            {
                'description': 'Null character as whitespace in display_resolution',
                'display_resolution': '"800\x00600"',
            },
            {
                'description': 'Numbers with various unicode digit characters in display_resolution',
                'display_resolution': '①❻➑０X𝟙𝟎𝟱𝟬',
            },
        ]

        for case in cases:
            with self.subTest(case['description']):
                with open(self.config_file_path, mode='w') as config_file:
                    config_file.write(config_file_contents_template.format(case['display_resolution']))

                self.assertRaisesRegex(
                    ValueError,
                    r"^Cannot parse setting for 'display_resolution'\.$",
                    configuration.Configuration,
                    self.config_directory_path
                )

    def test_configuration_with_out_of_range_values(self) -> None:
        cases: list[dict[str, str]] = [
            {
                'description': 'Infinite vcom value #1',
                'config_file_contents': (
                    'vcom = inf\n'
                    "display_resolution = 1872x1404\n"
                    'refresh_timeout = 300.0\n'
                    'video_directory = /videos\n'
                ),
            },
            {
                'description': 'Infinite vcom value #2',
                'config_file_contents': (
                    'vcom = -inf\n'
                    "display_resolution = 1872x1404\n"
                    'refresh_timeout = 300.0\n'
                    'video_directory = /videos\n'
                ),
            },
            {
                'description': 'Zero screen width in display_resolution',
                'config_file_contents': (
                    'vcom = -1.48\n'
                    "display_resolution = 0x1404\n"
                    'refresh_timeout = 300.0\n'
                    'video_directory = /videos\n'
                ),
            },
            {
                'description': 'Zero screen height in display_resolution',
                'config_file_contents': (
                    'vcom = -1.48\n'
                    "display_resolution = 1872x0\n"
                    'refresh_timeout = 300.0\n'
                    'video_directory = /videos\n'
                ),
            },
            {
                'description': 'Negative refresh_timeout',
                'config_file_contents': (
                    'vcom = -1.48\n'
                    "display_resolution = 1872x1404\n"
                    'refresh_timeout = -0.001\n'
                    'video_directory = /videos\n'
                ),
            },
            {
                'description': 'Empty string for video_directory',
                'config_file_contents': (
                    'vcom = -1.48\n'
                    "display_resolution = 1872x1404\n"
                    'refresh_timeout = 300.0\n'
                    'video_directory = ""\n'
                ),
            },
        ]

        for case in cases:
            with self.subTest(case['description']):
                with open(self.config_file_path, 'w') as config_file:
                    config_file.write(case['config_file_contents'])

                self.assertRaisesRegex(
                    ValueError,
                    r"^Configuration value out of permitted range\.$",
                    configuration.Configuration,
                    self.config_directory_path
                )
