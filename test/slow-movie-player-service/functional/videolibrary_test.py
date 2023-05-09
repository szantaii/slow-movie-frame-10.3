from module_helper import get_module_from_file
from unittest import TestCase
import tempfile
import os
import numpy
import cv2
import re
from typing import Any

video = get_module_from_file('../../src/slow-movie-player-service/video.py')
skip = get_module_from_file('../../src/slow-movie-player-service/skip.py')
videolibrary = get_module_from_file('../../src/slow-movie-player-service/videolibrary.py')


class VideoLibraryTest(TestCase):
    TEST_VIDEO_FILE_EXTENSIONS = (
        '.avi',
        '.mkv',
    )
    VIDEO_LIBRARY_FILE_NAME = 'videos.json'
    VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE = '{{{}\n}}'
    VIDEO_LIBRARY_ENTRY_TEMPLATE = (
        '\n'
        '    "{}": {{\n'
        '        "frame_count": {},\n'
        '        "duration": {},\n'
        '        "next_frame": {},\n'
        '        "next_timestamp": {}\n'
        '    }}'
    )

    def setUp(self) -> None:
        super().setUp()

        self.video_directory_path = tempfile.mkdtemp()
        self.video_library_file_path = os.path.join(self.video_directory_path, self.__class__.VIDEO_LIBRARY_FILE_NAME)

    def tearDown(self) -> None:
        for directory, _, files in os.walk(self.video_directory_path):
            for file_name in files:
                file_path = os.path.join(directory, file_name)

                if file_path.endswith(self.__class__.TEST_VIDEO_FILE_EXTENSIONS):
                    os.remove(file_path)

        if os.path.exists(self.video_library_file_path):
            os.remove(self.video_library_file_path)

        for directory in [directory_paths for directory_paths, _, _ in os.walk(self.video_directory_path)][::-1]:
            os.rmdir(directory)

        super().tearDown()

    def assert_file_contents_equals(self, file_path: str, expected_file_contents: str) -> None:
        with open(file_path, mode='r') as file:
            file_contents = file.read()

        self.assertEqual(file_contents, expected_file_contents)

    def create_video_in_video_directory(
        self,
        name: str,
        fps: int = 1,
        frame_count: int = 3,
        size: tuple[int, int] = (320, 240)
    ) -> dict[str, Any]:

        video_file_path = os.path.join(self.video_directory_path, name)
        vid = cv2.VideoWriter(video_file_path, 0, fps, size)

        if frame_count > 0:
            frame_shape = size[::-1] + (3,)
            red_frame = numpy.full(frame_shape, [0, 0, 255], dtype=numpy.uint8)
            green_frame = numpy.full(frame_shape, [0, 255, 0], dtype=numpy.uint8)
            blue_frame = numpy.full(frame_shape, [255, 0, 0], dtype=numpy.uint8)

            for i in range(frame_count):
                if i % 3 == 0:
                    vid.write(red_frame)
                elif i % 3 == 1:
                    vid.write(green_frame)
                else:
                    vid.write(blue_frame)

        vid.release()

        return {
            'file_path': video_file_path,
            'frame_count': frame_count,
            'duration': frame_count / fps * 1000.0 if frame_count and fps else 0.0
        }

    def test_load_video_library_from_file(self):
        video_file_properties = self.create_video_in_video_directory('video.mkv')
        expected_video_library_file_contents = (
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties.values(), 111, 999.9)
            )
        )

        with open(self.video_library_file_path, mode='w') as video_library_file:
            video_library_file.write(expected_video_library_file_contents)

        self.assert_file_contents_equals(self.video_library_file_path, expected_video_library_file_contents)

        videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(self.video_library_file_path, expected_video_library_file_contents)

    def test_load_video_library_from_invalid_file(self):
        self.assertFalse(os.path.exists(self.video_library_file_path))

        invalid_video_library_file_contents = '{Hello, World!}'

        with open(self.video_library_file_path, mode='w') as video_library_file:
            video_library_file.write(invalid_video_library_file_contents)

        self.assert_file_contents_equals(self.video_library_file_path, invalid_video_library_file_contents)
        self.assertRaisesRegex(
            ValueError,
            (
                r"^"
                r"Cannot load video library from '{}'\. "
                r"It is recommended to check for backup \('.bak'\) and temporary \('.tmp'\) files in '{}' "
                r"for manually recovering video library data\. "
                r"See details for easier debugging: '.+'\."
                r"$"
            ).format(
                re.escape(self.video_library_file_path),
                re.escape(self.video_directory_path)
            ),
            videolibrary.VideoLibrary,
            self.video_directory_path
        )
        self.assert_file_contents_equals(self.video_library_file_path, invalid_video_library_file_contents)

    def test_video_discovery_with_non_existing_video_directory(self):
        non_existing_video_directory_path = '/hopefully/this/directory/does/not/exist'

        self.assertFalse(os.path.exists(non_existing_video_directory_path))
        self.assertRaisesRegex(
            FileNotFoundError,
            r"^Video directory '{}' does not exist\.$".format(non_existing_video_directory_path),
            videolibrary.VideoLibrary,
            non_existing_video_directory_path
        )
        self.assertFalse(os.path.exists(non_existing_video_directory_path))

    def test_video_discovery_with_empty_video_directory(self):
        self.assertFalse(os.path.exists(self.video_library_file_path))

        videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(self.video_library_file_path, '{}')

    def test_video_discovery_with_a_single_video_file(self):
        test_video_file_properties = self.create_video_in_video_directory('test_video.avi')

        self.assertFalse(os.path.exists(self.video_library_file_path))

        videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*test_video_file_properties.values(), 0, 0.0)
            )
        )

    def test_video_discovery_with_multiple_video_files_and_subdirectories(self):
        subdirectory_name_1 = 'c_subdirectory'
        subdirectory_name_2 = 'd_subdirectory/and_another'

        video_properties_1 = self.create_video_in_video_directory('a_video.mkv')
        video_properties_2 = self.create_video_in_video_directory('a_video.avi')
        video_properties_3 = self.create_video_in_video_directory('b_video.mkv')
        os.mkdir(os.path.join(self.video_directory_path, subdirectory_name_1))
        video_properties_4 = self.create_video_in_video_directory(os.path.join(subdirectory_name_1, 'a_video.avi'))
        os.makedirs(os.path.join(self.video_directory_path, subdirectory_name_2))
        video_properties_5 = self.create_video_in_video_directory(os.path.join(subdirectory_name_2, 'a_video.mkv'))
        video_properties_6 = self.create_video_in_video_directory('e_video.mkv')

        self.assertFalse(os.path.exists(self.video_library_file_path))

        videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                '{},{},{},{},{},{}'.format(
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_properties_2.values(), 0, 0.0),
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_properties_1.values(), 0, 0.0),
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_properties_3.values(), 0, 0.0),
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_properties_4.values(), 0, 0.0),
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_properties_5.values(), 0, 0.0),
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_properties_6.values(), 0, 0.0)
                )
            )
        )

    def test_video_discovery_with_video_file_already_in_library_was_deleted(self):
        video_properties_1 = self.create_video_in_video_directory('a.avi')
        video_properties_2 = self.create_video_in_video_directory('b.mkv')

        self.assertFalse(os.path.exists(self.video_library_file_path))

        videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                '{},{}'.format(
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_properties_1.values(), 0, 0.0),
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_properties_2.values(), 0, 0.0)
                )
            )
        )

        os.remove(video_properties_1['file_path'])

        videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_properties_2.values(), 0, 0.0)
            )
        )

    def test_video_discovery_with_new_video_file_which_was_not_yet_in_library(self):
        video_file_properties_1 = self.create_video_in_video_directory('b_video.mkv')

        self.assertFalse(os.path.exists(self.video_library_file_path))

        videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_1.values(), 0, 0.0)
            )
        )

        video_file_properties_2 = self.create_video_in_video_directory('a_video.avi')

        videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                '{},{}'.format(
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_1.values(), 0, 0.0),
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_2.values(), 0, 0.0)
                )
            )
        )

    def test_video_discovery_with_video_file_replaced_with_same_name(self):
        video_file_name = 'video.avi'
        video_file_properties_1 = self.create_video_in_video_directory(video_file_name)

        self.assertFalse(os.path.exists(self.video_library_file_path))

        videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_1.values(), 0, 0.0)
            )
        )

        video_file_properties_2 = self.create_video_in_video_directory(video_file_name, fps=2)

        videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_2.values(), 0, 0.0)
            )
        )

        video_file_properties_3 = self.create_video_in_video_directory(video_file_name, fps=2, frame_count=4)

        videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_3.values(), 0, 0.0)
            )
        )

    def test_get_next_frame(self):
        self.create_video_in_video_directory('video.mkv')

        self.assertFalse(os.path.exists(self.video_library_file_path))

        video_library = videolibrary.VideoLibrary(self.video_directory_path)

        for expected_color in [[0, 0, 255], [0, 255, 0], [255, 0, 0]]:
            expected_video_frame = numpy.full((240, 320, 3), expected_color, dtype=numpy.uint8)
            video_frame = video_library.get_next_frame()

            # Due to the video encoding, not all the colors will be completely the
            # same as were in the original video frames. Therefore, it is necessary
            # to check whether the color values are within a small tolerance.
            self.assertTrue(numpy.allclose(video_frame, expected_video_frame, rtol=0, atol=5))

    def test_get_next_frame_with_frame_skip(self):
        video_file_properties = self.create_video_in_video_directory('video.mkv')

        self.assertFalse(os.path.exists(self.video_library_file_path))

        videolibrary.VideoLibrary(self.video_directory_path).get_next_frame(skip.FrameSkip(2))

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties.values(), 2, 2000.0)
            )
        )

    def test_get_next_frame_with_time_skip(self):
        video_file_properties = self.create_video_in_video_directory('video.mkv')

        self.assertFalse(os.path.exists(self.video_library_file_path))

        videolibrary.VideoLibrary(self.video_directory_path).get_next_frame(skip.TimeSkip(500.0))

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties.values(), 0, 500.0)
            )
        )

    def test_get_next_frame_with_incorrect_type_arguments(self):
        video_file_properties = self.create_video_in_video_directory('video.mkv')
        expected_video_library_file_contents = (
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties.values(), 0, 0.0)
            )
        )

        incorrect_type_arguments = (1, 1000.0)

        for incorrect_type_argument in incorrect_type_arguments:
            with self.subTest(incorrect_type_argument=incorrect_type_argument):
                if os.path.exists(self.video_library_file_path):
                    os.remove(self.video_library_file_path)

                video_library = videolibrary.VideoLibrary(self.video_directory_path)

                self.assert_file_contents_equals(self.video_library_file_path, expected_video_library_file_contents)
                self.assertRaisesRegex(
                    TypeError,
                    (
                        r"^Argument 'skip' is of type '{}', "
                        r"but should be of type '<class 'skip\.FrameSkip'>' or '<class 'skip\.TimeSkip'>' instead\."
                    ).format(
                        type(incorrect_type_argument)
                    ),
                    video_library.get_next_frame,
                    incorrect_type_argument
                )
                self.assert_file_contents_equals(self.video_library_file_path, expected_video_library_file_contents)

    def test_get_frame_with_empty_video_library(self):
        expected_video_library_file_contents = '{}'

        self.assertFalse(os.path.exists(self.video_library_file_path))

        video_library = videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(self.video_library_file_path, expected_video_library_file_contents)
        self.assertRaisesRegex(
            RuntimeError,
            r"^Cannot get frame from empty video library!$",
            video_library.get_next_frame
        )
        self.assert_file_contents_equals(self.video_library_file_path, expected_video_library_file_contents)

    def test_restart_from_beginning_after_reading_last_frame(self):
        video_file_properties_1 = self.create_video_in_video_directory('video_1.avi')
        video_file_properties_2 = self.create_video_in_video_directory('video_2.avi')

        self.assertFalse(os.path.exists(self.video_library_file_path))

        video_library = videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                '{},{}'.format(
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_1.values(), 0, 0.0),
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_2.values(), 0, 0.0)
                )
            )
        )

        video_library.get_next_frame(skip.FrameSkip(3))

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                '{},{}'.format(
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_1.values(), 3, 3000.0),
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_2.values(), 0, 0.0)
                )
            )
        )

        video_library.get_next_frame(skip.TimeSkip(3000.0))

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                '{},{}'.format(
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_1.values(), 3, 3000.0),
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_2.values(), 3, 3000.0)
                )
            )
        )

        video_library.get_next_frame(skip.TimeSkip(0.001))

        self.assert_file_contents_equals(
            self.video_library_file_path,
            self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
                '{},{}'.format(
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_1.values(), 0, 0.001),
                    self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_2.values(), 0, 0.0)
                )
            )
        )

    def test_get_random_frame(self) -> None:
        video_file_properties_1 = self.create_video_in_video_directory('video_1.mkv')
        video_file_properties_2 = self.create_video_in_video_directory('video_2.avi')
        initial_video_library_file_contents = self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
            '{},{}'.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_1.values(), 0, 0.0),
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_2.values(), 0, 0.0)
            )
        )
        video_library_file_contents_after_second_frame = self.__class__.VIDEO_LIBRARY_FILE_CONTENTS_TEMPLATE.format(
            '{},{}'.format(
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_1.values(), 2, 2000.0),
                self.__class__.VIDEO_LIBRARY_ENTRY_TEMPLATE.format(*video_file_properties_2.values(), 0, 0.0)
            )
        )
        expected_video_frames = []

        for expected_color in [[0, 0, 255], [0, 255, 0], [255, 0, 0]]:
            expected_video_frames.append(numpy.full((240, 320, 3), expected_color, dtype=numpy.uint8))

        def assert_random_video_frame_in_expected_frames(random_video_frame: numpy.ndarray) -> None:
            self.assertEqual(
                [
                    False,
                    False,
                    True,
                ],
                sorted(
                    [
                        numpy.allclose(random_video_frame, expected_video_frames[0], rtol=0, atol=5),
                        numpy.allclose(random_video_frame, expected_video_frames[1], rtol=0, atol=5),
                        numpy.allclose(random_video_frame, expected_video_frames[2], rtol=0, atol=5),
                    ]
                )
            )

        self.assertFalse(os.path.exists(self.video_library_file_path))

        video_library = videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(self.video_library_file_path, initial_video_library_file_contents)

        random_video_frame_1 = video_library.get_random_frame()

        assert_random_video_frame_in_expected_frames(random_video_frame_1)

        self.assert_file_contents_equals(self.video_library_file_path, initial_video_library_file_contents)

        video_library.get_next_frame(skip.TimeSkip(2000.0))

        self.assert_file_contents_equals(self.video_library_file_path, video_library_file_contents_after_second_frame)

        random_video_frame_2 = video_library.get_random_frame()

        assert_random_video_frame_in_expected_frames(random_video_frame_2)

        self.assert_file_contents_equals(self.video_library_file_path, video_library_file_contents_after_second_frame)

    def test_get_random_frame_with_empty_video_library(self) -> None:
        expected_video_library_file_contents = '{}'

        self.assertFalse(os.path.exists(self.video_library_file_path))

        video_library = videolibrary.VideoLibrary(self.video_directory_path)

        self.assert_file_contents_equals(self.video_library_file_path, expected_video_library_file_contents)
        self.assertRaisesRegex(
            RuntimeError,
            r"^Cannot get frame from empty video library!$",
            video_library.get_random_frame
        )
        self.assert_file_contents_equals(self.video_library_file_path, expected_video_library_file_contents)
