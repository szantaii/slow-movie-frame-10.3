from module_helper import get_module_from_file
from unittest import TestCase
from unittest.mock import call, Mock, mock_open, patch
from collections import OrderedDict
import os
import json

videolibrary = get_module_from_file('../../src/slow-movie-player-service/videolibrary.py')


class VideoLibraryTest(TestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch('os.unlink', spec=os.unlink)
    @patch('os.rename', spec=os.rename)
    @patch('os.access', spec=os.access)
    @patch('os.close', spec=os.close)
    @patch('os.fsync', spec=os.fsync)
    @patch('json.dumps', spec=json.dumps)
    @patch('os.write', spec=os.write)
    @patch('os.F_OK')
    @patch('os.O_WRONLY')
    @patch('os.O_CREAT')
    @patch('os.open', spec=os.open)
    @patch('os.walk', spec=os.walk)
    @patch('os.path.join', spec=os.path.join)
    @patch('os.path.exists', spec=os.path.exists)
    def test_save_to_file(
        self,
        os_path_exists_function_mock: Mock,
        os_path_join_function_mock: Mock,
        os_walk_function_mock: Mock,
        os_open_function_mock: Mock,
        os_create_file_flag_mock: Mock,
        os_write_only_flag_mock: Mock,
        os_file_exists_flag_mock: Mock,
        os_write_function_mock: Mock,
        json_dumps_function_mock: Mock,
        os_fsync_function_mock: Mock,
        os_close_function_mock: Mock,
        os_access_function_mock: Mock,
        os_rename_function_mock: Mock,
        os_unlink_function_mock: Mock,
        builtins_open_function_mock: Mock
    ) -> None:

        video_directory_path = '/path/to/video/directory'
        video_library_file_path = '{}/{}'.format(
            video_directory_path,
            videolibrary.VideoLibrary.VIDEO_LIBRARY_FILE_NAME
        )
        temp_video_library_file_path = '{}{}'.format(
            video_library_file_path,
            videolibrary.VideoLibrary.TEMPORARY_FILE_EXTENSION
        )
        backup_video_library_file_path = '{}{}'.format(
            video_library_file_path,
            videolibrary.VideoLibrary.BACKUP_FILE_EXTENSION
        )

        os_path_exists_function_mock.side_effect = {
            video_directory_path: True,
            video_library_file_path: False
        }.get
        os_path_join_function_mock.side_effect = lambda str1, str2: '{}/{}'.format(str1, str2)
        os_walk_function_mock.return_value = []

        os_open_flag_mock = os_create_file_flag_mock | os_write_only_flag_mock
        temp_video_library_file_mock = os_open_function_mock(temp_video_library_file_path, os_open_flag_mock)
        json_bytestring_mock = json_dumps_function_mock(OrderedDict(), ensure_ascii=False, indent=4).encode()
        json_string_mock = json_dumps_function_mock(OrderedDict(), ensure_ascii=False, indent=4)

        os_open_function_mock.reset_mock()
        json_dumps_function_mock.reset_mock()

        expected_os_path_exists_function_mock_calls = [
            call(video_directory_path),
            call(video_library_file_path),
        ]
        expected_os_walk_function_mock_calls = [
            call(video_directory_path),
        ]
        expected_os_open_function_mock_calls = [
            call(temp_video_library_file_path, os_open_flag_mock),
        ]
        expected_os_write_function_mock_calls = [
            call(temp_video_library_file_mock, json_bytestring_mock),
        ]
        expected_os_fsync_function_mock_calls = [
            call(temp_video_library_file_mock),
        ]
        expected_os_close_function_mock_calls = expected_os_fsync_function_mock_calls

        json_string_mock.__ne__.side_effect = [True]

        self.assertListEqual(os_path_exists_function_mock.mock_calls, [])
        self.assertListEqual(os_walk_function_mock.mock_calls, [])
        self.assertListEqual(os_open_function_mock.mock_calls, [])
        self.assertListEqual(os_write_function_mock.mock_calls, [])
        self.assertListEqual(json_dumps_function_mock.mock_calls, [])
        self.assertListEqual(os_fsync_function_mock.mock_calls, [])
        self.assertListEqual(os_close_function_mock.mock_calls, [])
        self.assertListEqual(os_access_function_mock.mock_calls, [])
        self.assertListEqual(os_rename_function_mock.mock_calls, [])
        self.assertListEqual(os_unlink_function_mock.mock_calls, [])
        self.assertListEqual(builtins_open_function_mock.mock_calls, [])

        self.assertRaisesRegex(
            ValueError,
            (
                r"^Cannot save video library to '{}'\. "
                r"It is recommended to check for backup \('\.bak'\) and "
                r"temporary \('\.tmp'\) files in '{}' "
                r"for manually recovering video library data\.$"
            ).format(
                video_library_file_path,
                video_directory_path
            ),
            videolibrary.VideoLibrary,
            video_directory_path
        )

        self.assertListEqual(os_path_exists_function_mock.mock_calls, expected_os_path_exists_function_mock_calls)
        self.assertListEqual(os_walk_function_mock.mock_calls, expected_os_walk_function_mock_calls)
        self.assertListEqual(os_open_function_mock.mock_calls, expected_os_open_function_mock_calls)
        self.assertListEqual(os_write_function_mock.mock_calls, expected_os_write_function_mock_calls)
        self.assertListEqual(
            json_dumps_function_mock.mock_calls,
            [
                call(OrderedDict(), ensure_ascii=False, indent=4),
                call().encode('utf-8'),
                call(OrderedDict(), ensure_ascii=False, indent=4),
                call().__ne__(''),
            ]
        )
        self.assertListEqual(os_fsync_function_mock.mock_calls, expected_os_fsync_function_mock_calls)
        self.assertListEqual(os_close_function_mock.mock_calls, expected_os_close_function_mock_calls)
        self.assertListEqual(os_access_function_mock.mock_calls, [])
        self.assertListEqual(os_rename_function_mock.mock_calls, [])
        self.assertListEqual(os_unlink_function_mock.mock_calls, [])
        self.assertListEqual(
            builtins_open_function_mock.mock_calls,
            [
                call(temp_video_library_file_path, 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None),
            ]
        )

        os_path_exists_function_mock.reset_mock()
        os_path_join_function_mock.reset_mock()
        os_walk_function_mock.reset_mock()
        os_open_function_mock.reset_mock()
        os_create_file_flag_mock.reset_mock()
        os_write_only_flag_mock.reset_mock()
        os_file_exists_flag_mock.reset_mock()
        os_write_function_mock.reset_mock()
        json_dumps_function_mock.reset_mock()
        os_fsync_function_mock.reset_mock()
        os_close_function_mock.reset_mock()
        os_access_function_mock.reset_mock()
        os_rename_function_mock.reset_mock()
        os_unlink_function_mock.reset_mock()
        builtins_open_function_mock.reset_mock()

        json_string_mock.__ne__.side_effect = [False, True]

        self.assertListEqual(os_path_exists_function_mock.mock_calls, [])
        self.assertListEqual(os_walk_function_mock.mock_calls, [])
        self.assertListEqual(os_open_function_mock.mock_calls, [])
        self.assertListEqual(os_write_function_mock.mock_calls, [])
        self.assertListEqual(json_dumps_function_mock.mock_calls, [])
        self.assertListEqual(os_fsync_function_mock.mock_calls, [])
        self.assertListEqual(os_close_function_mock.mock_calls, [])
        self.assertListEqual(os_access_function_mock.mock_calls, [])
        self.assertListEqual(os_rename_function_mock.mock_calls, [])
        self.assertListEqual(os_unlink_function_mock.mock_calls, [])
        self.assertListEqual(builtins_open_function_mock.mock_calls, [])

        self.assertRaisesRegex(
            ValueError,
            (
                r"^Cannot save video library to '{}'\. "
                r"It is recommended to check for backup \('\.bak'\) and "
                r"temporary \('\.tmp'\) files in '{}' "
                r"for manually recovering video library data\.$"
            ).format(
                video_library_file_path,
                video_directory_path
            ),
            videolibrary.VideoLibrary,
            video_directory_path
        )

        self.assertListEqual(os_path_exists_function_mock.mock_calls, expected_os_path_exists_function_mock_calls)
        self.assertListEqual(os_walk_function_mock.mock_calls, expected_os_walk_function_mock_calls)
        self.assertListEqual(os_open_function_mock.mock_calls, expected_os_open_function_mock_calls)
        self.assertListEqual(os_write_function_mock.mock_calls, expected_os_write_function_mock_calls)
        self.assertListEqual(
            json_dumps_function_mock.mock_calls,
            [
                call(OrderedDict(), ensure_ascii=False, indent=4),
                call().encode('utf-8'),
                call(OrderedDict(), ensure_ascii=False, indent=4),
                call().__ne__(''),
                call(OrderedDict(), ensure_ascii=False, indent=4),
                call().__ne__(''),
            ]
        )
        self.assertListEqual(os_fsync_function_mock.mock_calls, expected_os_fsync_function_mock_calls)
        self.assertListEqual(os_close_function_mock.mock_calls, expected_os_close_function_mock_calls)
        self.assertListEqual(
            os_access_function_mock.mock_calls,
            [
                call(video_library_file_path, os_file_exists_flag_mock, follow_symlinks=False),
                call().__bool__(),
            ]
        )
        self.assertListEqual(
            os_rename_function_mock.mock_calls,
            [
                call(video_library_file_path, backup_video_library_file_path),
                call(temp_video_library_file_path, video_library_file_path),
            ]
        )
        self.assertListEqual(os_unlink_function_mock.mock_calls, [])
        self.assertListEqual(
            builtins_open_function_mock.mock_calls,
            [
                call(temp_video_library_file_path, 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None),
                call(video_library_file_path, 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None),
            ]
        )

        os_path_exists_function_mock.reset_mock()
        os_path_join_function_mock.reset_mock()
        os_walk_function_mock.reset_mock()
        os_open_function_mock.reset_mock()
        os_create_file_flag_mock.reset_mock()
        os_write_only_flag_mock.reset_mock()
        os_file_exists_flag_mock.reset_mock()
        os_write_function_mock.reset_mock()
        json_dumps_function_mock.reset_mock()
        os_fsync_function_mock.reset_mock()
        os_close_function_mock.reset_mock()
        os_access_function_mock.reset_mock()
        os_rename_function_mock.reset_mock()
        os_unlink_function_mock.reset_mock()
        builtins_open_function_mock.reset_mock()

        json_string_mock.__ne__.side_effect = [False, False]

        self.assertListEqual(os_path_exists_function_mock.mock_calls, [])
        self.assertListEqual(os_walk_function_mock.mock_calls, [])
        self.assertListEqual(os_open_function_mock.mock_calls, [])
        self.assertListEqual(os_write_function_mock.mock_calls, [])
        self.assertListEqual(json_dumps_function_mock.mock_calls, [])
        self.assertListEqual(os_fsync_function_mock.mock_calls, [])
        self.assertListEqual(os_close_function_mock.mock_calls, [])
        self.assertListEqual(os_access_function_mock.mock_calls, [])
        self.assertListEqual(os_rename_function_mock.mock_calls, [])
        self.assertListEqual(os_unlink_function_mock.mock_calls, [])
        self.assertListEqual(builtins_open_function_mock.mock_calls, [])

        try:
            videolibrary.VideoLibrary(video_directory_path)
        except ValueError:
            self.fail('ValueError was raised unexpectedly!')

        self.assertListEqual(os_path_exists_function_mock.mock_calls, expected_os_path_exists_function_mock_calls)
        self.assertListEqual(os_walk_function_mock.mock_calls, expected_os_walk_function_mock_calls)
        self.assertListEqual(os_open_function_mock.mock_calls, expected_os_open_function_mock_calls)
        self.assertListEqual(os_write_function_mock.mock_calls, expected_os_write_function_mock_calls)
        self.assertListEqual(
            json_dumps_function_mock.mock_calls,
            [
                call(OrderedDict(), ensure_ascii=False, indent=4),
                call().encode('utf-8'),
                call(OrderedDict(), ensure_ascii=False, indent=4),
                call().__ne__(''),
                call(OrderedDict(), ensure_ascii=False, indent=4),
                call().__ne__(''),
            ]
        )
        self.assertListEqual(os_fsync_function_mock.mock_calls, expected_os_fsync_function_mock_calls)
        self.assertListEqual(os_close_function_mock.mock_calls, expected_os_close_function_mock_calls)
        self.assertListEqual(
            os_access_function_mock.mock_calls,
            [
                call(video_library_file_path, os_file_exists_flag_mock, follow_symlinks=False),
                call().__bool__(),
                call(backup_video_library_file_path, os_file_exists_flag_mock, follow_symlinks=False),
                call().__bool__(),
            ]
        )
        self.assertListEqual(
            os_rename_function_mock.mock_calls,
            [
                call(video_library_file_path, backup_video_library_file_path),
                call(temp_video_library_file_path, video_library_file_path),
            ]
        )
        self.assertListEqual(
            os_unlink_function_mock.mock_calls,
            [
                call(backup_video_library_file_path),
            ]
        )
        self.assertListEqual(
            builtins_open_function_mock.mock_calls,
            [
                call(temp_video_library_file_path, 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None),
                call(video_library_file_path, 'r'),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None),
            ]
        )
