from module_helper import get_module_from_file
import os
from unittest import TestCase
from unittest.mock import call, Mock, mock_open, patch

skip = get_module_from_file('../../src/slow-movie-player-service/skip.py')
grayscalemethod = get_module_from_file('../../src/slow-movie-player-service/grayscalemethod.py')
configuration = get_module_from_file('../../src/slow-movie-player-service/configuration.py')


class ConfigurationTest(TestCase):
    CONFIG_DIRECTORY_PATH = '/path/to/config/directory'
    CONFIG_FILE_NAME = 'test_config_file_name.conf'

    @patch('configuration.GrayscaleMethod', spec=grayscalemethod.GrayscaleMethod)
    @patch('configuration.TimeSkip', spec=skip.TimeSkip)
    @patch('configuration.FrameSkip', spec=skip.FrameSkip)
    @patch('os.scandir', spec=os.scandir)
    def test_configuration_with_empty_config_directory(
        self,
        scandir_function_mock: Mock,
        frame_skip_mock: Mock,
        time_skip_mock: Mock,
        grayscale_method_mock: Mock
    ) -> None:

        scandir_function_mock.return_value = []

        expected_scandir_function_mock_calls = [
            call(self.__class__.CONFIG_DIRECTORY_PATH),
        ]
        expected_frame_skip_mock_calls = [
            call(1),
        ]

        self.assertListEqual(scandir_function_mock.mock_calls, [])
        self.assertListEqual(frame_skip_mock.mock_calls, [])
        self.assertListEqual(time_skip_mock.mock_calls, [])
        self.assertListEqual(grayscale_method_mock.mock_calls, [])

        self.assertRaisesRegex(
            FileNotFoundError,
            r"^No config file found in '{}'\.$".format(self.__class__.CONFIG_DIRECTORY_PATH),
            configuration.Configuration,
            self.__class__.CONFIG_DIRECTORY_PATH
        )

        self.assertListEqual(scandir_function_mock.mock_calls, expected_scandir_function_mock_calls)
        self.assertListEqual(frame_skip_mock.mock_calls, expected_frame_skip_mock_calls)
        self.assertListEqual(time_skip_mock.mock_calls, [])
        self.assertListEqual(grayscale_method_mock.mock_calls, [])

    @patch('configuration.GrayscaleMethod', spec=grayscalemethod.GrayscaleMethod)
    @patch('configuration.TimeSkip', spec=skip.TimeSkip)
    @patch('configuration.FrameSkip', spec=skip.FrameSkip)
    @patch('os.scandir', spec=os.scandir)
    def test_configuration_when_no_config_file_found(
        self,
        scandir_function_mock: Mock,
        frame_skip_mock: Mock,
        time_skip_mock: Mock,
        grayscale_method_mock: Mock
    ) -> None:

        dir_entry_mock_1 = Mock(spec=os.DirEntry)
        dir_entry_mock_1.is_file.return_value = False

        dir_entry_mock_2 = Mock(spec=os.DirEntry)
        dir_entry_mock_2.is_file.return_value = True
        dir_entry_mock_2.name = 'file_with_incorrect.extension'

        scandir_function_mock.return_value = [
            dir_entry_mock_1, dir_entry_mock_2
        ]

        expected_scandir_function_mock_calls = [
            call(self.__class__.CONFIG_DIRECTORY_PATH),
        ]
        expected_frame_skip_mock_calls = [
            call(1),
        ]
        expected_dir_entry_1_mock_calls = [
            call.is_file(),
        ]
        expected_dir_entry_2_mock_calls = [
            call.is_file(),
        ]

        self.assertListEqual(scandir_function_mock.mock_calls, [])
        self.assertListEqual(frame_skip_mock.mock_calls, [])
        self.assertListEqual(time_skip_mock.mock_calls, [])
        self.assertListEqual(grayscale_method_mock.mock_calls, [])
        self.assertListEqual(dir_entry_mock_1.mock_calls, [])
        self.assertListEqual(dir_entry_mock_2.mock_calls, [])

        self.assertRaisesRegex(
            FileNotFoundError,
            r"^No config file found in '{}'\.$".format(self.__class__.CONFIG_DIRECTORY_PATH),
            configuration.Configuration,
            self.__class__.CONFIG_DIRECTORY_PATH
        )

        self.assertListEqual(scandir_function_mock.mock_calls, expected_scandir_function_mock_calls)
        self.assertListEqual(frame_skip_mock.mock_calls, expected_frame_skip_mock_calls)
        self.assertListEqual(time_skip_mock.mock_calls, [])
        self.assertListEqual(grayscale_method_mock.mock_calls, [])
        self.assertListEqual(dir_entry_mock_1.mock_calls, expected_dir_entry_1_mock_calls)
        self.assertListEqual(dir_entry_mock_2.mock_calls, expected_dir_entry_2_mock_calls)

    @patch('configuration.GrayscaleMethod', spec=grayscalemethod.GrayscaleMethod)
    @patch('configuration.TimeSkip', spec=skip.TimeSkip)
    @patch('configuration.FrameSkip', spec=skip.FrameSkip)
    @patch('os.scandir', spec=os.scandir)
    @patch('os.path.join', spec=os.path.join)
    def test_configuration_with_default_config(
        self,
        path_join_function_mock: Mock,
        scandir_function_mock: Mock,
        frame_skip_mock: Mock,
        time_skip_mock: Mock,
        grayscale_method_mock: Mock,
    ) -> None:

        vcom_value = -1.48
        screen_width_value = 1872
        screen_height_value = 1404
        display_resolution_value = '{} x {}'.format(
            screen_width_value,
            screen_height_value
        )
        refresh_timeout_value = 180.0
        video_directory_value = '/videos'
        frame_skip_value = 3
        time_skip_value = 100.0
        grayscale_method_value = 'Rec709Luma'
        random_frame_value = False

        default_configuration_string = (
            'vcom = {vcom_value}\n'
            'display_resolution = {display_resolution_value}\n'
            'refresh_timeout = {refresh_timeout_value}\n'
            "video_directory = '{video_directory_value}'\n"
            'frame_skip = {frame_skip_value}\n'
            'time_skip = {time_skip_value}\n'
            'grayscale_method = "{grayscale_method_value}"\n'
            'random_frame = {random_frame_value}\n'
        ).format(
            vcom_value=vcom_value,
            display_resolution_value=display_resolution_value,
            refresh_timeout_value=refresh_timeout_value,
            video_directory_value=video_directory_value,
            frame_skip_value=frame_skip_value,
            time_skip_value=time_skip_value,
            grayscale_method_value=grayscale_method_value,
            random_frame_value=('true' if random_frame_value else 'false')
        )

        config_file_absolute_path = '{}/{}'.format(
            self.__class__.CONFIG_DIRECTORY_PATH,
            self.__class__.CONFIG_FILE_NAME
        )

        path_join_function_mock.return_value = config_file_absolute_path

        dir_entry_mock = Mock(spec=os.DirEntry)
        dir_entry_mock.is_file.return_value = True
        dir_entry_mock.name = self.__class__.CONFIG_FILE_NAME

        scandir_function_mock.return_value = [
            dir_entry_mock,
        ]

        expected_path_join_function_mock_calls = [
            call(self.__class__.CONFIG_DIRECTORY_PATH, self.__class__.CONFIG_FILE_NAME),
        ]
        expected_scandir_function_mock_calls = [
            call(self.__class__.CONFIG_DIRECTORY_PATH),
        ]
        expected_frame_skip_mock_calls = [
            call(1),
        ]
        expected_time_skip_mock_calls = [
            call(100.0),
        ]
        expected_grayscale_method_calls = [
            call('Rec709Luma'),
        ]
        expected_dir_entry_mock_calls = [
            call.is_file(),
        ]
        expected_open_function_mock_calls = [
            call(config_file_absolute_path, 'r'),
            call().__enter__(),
            call().read(),
            call().__exit__(None, None, None),
        ]

        self.assertListEqual(path_join_function_mock.mock_calls, [])
        self.assertListEqual(scandir_function_mock.mock_calls, [])
        self.assertListEqual(frame_skip_mock.mock_calls, [])
        self.assertListEqual(time_skip_mock.mock_calls, [])
        self.assertListEqual(grayscale_method_mock.mock_calls, [])
        self.assertListEqual(dir_entry_mock.mock_calls, [])

        with patch('builtins.open', mock_open(read_data=default_configuration_string)) as open_function_mock:
            config = configuration.Configuration(self.__class__.CONFIG_DIRECTORY_PATH)

        self.assertEqual(config.vcom, vcom_value)
        self.assertEqual(config.screen_width, screen_width_value)
        self.assertEqual(config.screen_height, screen_height_value)
        self.assertEqual(config.refresh_timeout, refresh_timeout_value)
        self.assertEqual(config.video_directory, video_directory_value)
        self.assertEqual(config.random_frame, random_frame_value)

        self.assertListEqual(path_join_function_mock.mock_calls, expected_path_join_function_mock_calls)
        self.assertListEqual(scandir_function_mock.mock_calls, expected_scandir_function_mock_calls)
        self.assertListEqual(frame_skip_mock.mock_calls, expected_frame_skip_mock_calls)
        self.assertListEqual(time_skip_mock.mock_calls, expected_time_skip_mock_calls)
        self.assertListEqual(grayscale_method_mock.mock_calls, expected_grayscale_method_calls)
        self.assertListEqual(dir_entry_mock.mock_calls, expected_dir_entry_mock_calls)
        self.assertListEqual(open_function_mock.mock_calls, expected_open_function_mock_calls)
