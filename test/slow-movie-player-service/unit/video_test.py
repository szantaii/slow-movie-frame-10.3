from module_helper import get_module_from_file
from unittest import TestCase
from unittest.mock import call, Mock, patch
import cv2
import sys
import re

video = get_module_from_file('../../src/slow-movie-player-service/video.py')


class VideoTest(TestCase):
    VIDEO_FILE_PATH = '/path/to/video/file'

    @patch('cv2.CAP_PROP_FPS')
    @patch('cv2.VideoCapture', spec=cv2.VideoCapture)
    def test_get_frame_rate(self, video_capture_mock: Mock, fps_property_mock: Mock) -> None:
        frame_rate = 25.0
        video_mock = video_capture_mock(self.__class__.VIDEO_FILE_PATH)

        video_mock.get.side_effect = {
            fps_property_mock: frame_rate,
        }.get

        video_capture_mock.reset_mock()

        expected_frame_rate = frame_rate
        expected_video_capture_mock_calls = [
            call(self.__class__.VIDEO_FILE_PATH),
            call().get(fps_property_mock),
            call().release(),
        ]
        expected_video_mock_calls = [
            call.get(fps_property_mock),
            call.release(),
        ]

        self.assertListEqual(video_capture_mock.mock_calls, [])
        self.assertListEqual(video_mock.mock_calls, [])

        self.assertEqual(
            video.Video(self.__class__.VIDEO_FILE_PATH).get_frame_rate(),
            expected_frame_rate
        )

        self.assertListEqual(video_capture_mock.mock_calls, expected_video_capture_mock_calls)
        self.assertListEqual(video_mock.mock_calls, expected_video_mock_calls)

    @patch('cv2.CAP_PROP_FPS')
    @patch('cv2.CAP_PROP_FRAME_COUNT')
    @patch('cv2.VideoCapture', spec=cv2.VideoCapture)
    def test_get_stats(
        self,
        video_capture_mock: Mock,
        frame_count_property_mock: Mock,
        fps_property_mock: Mock
    ) -> None:

        frame_rate = 25.0
        frame_count = 25000

        video_mock = video_capture_mock(self.__class__.VIDEO_FILE_PATH)

        video_mock.get.side_effect = {
            frame_count_property_mock: frame_count,
            fps_property_mock: frame_rate,
        }.get

        video_capture_mock.reset_mock()

        expected_frame_count = frame_count
        expected_duration = 1000000.0  # milliseconds
        expected_video_capture_mock_calls = [
            call(self.__class__.VIDEO_FILE_PATH),
            call().get(fps_property_mock),
            call().get(frame_count_property_mock),
            call().release(),
        ]
        expected_video_mock_calls = [
            call.get(fps_property_mock),
            call.get(frame_count_property_mock),
            call.release(),
        ]

        self.assertListEqual(video_capture_mock.mock_calls, [])
        self.assertListEqual(video_mock.mock_calls, [])

        self.assertTupleEqual(
            video.Video(self.__class__.VIDEO_FILE_PATH).get_stats(),
            (expected_frame_count, expected_duration)
        )

        self.assertListEqual(video_capture_mock.mock_calls, expected_video_capture_mock_calls)
        self.assertListEqual(video_mock.mock_calls, expected_video_mock_calls)

    @patch('cv2.CAP_PROP_POS_FRAMES')
    @patch('cv2.CAP_PROP_POS_MSEC')
    @patch('cv2.VideoCapture', spec=cv2.VideoCapture)
    def test_get_frame(
        self,
        video_capture_mock: Mock,
        time_based_position_mock: Mock,
        frame_based_position_mock: Mock
    ) -> None:

        cases = (
            {
                'description': 'Get first frame by frame index',
                'position': 0,
                'frame_data': 'dummy data by frame index #1',
            },
            {
                'description': 'Get second frame by frame index',
                'position': 1,
                'frame_data': 'dummy data by frame index #2',
            },
            {
                'description': 'Get frame by very large frame index number',
                'position': int(sys.float_info.max),
                'frame_data': 'dummy data by frame index #3',
            },
            {
                'description': 'Get first frame by timestamp',
                'position': 0.0,  # milliseconds
                'frame_data': 'dummy data by timestamp #1',
            },
            {
                'description': 'Get second frame by timestamp',
                'position': sys.float_info.epsilon,  # milliseconds
                'frame_data': 'dummy data by timestamp #2',
            },
            {
                'description': 'Get frame exactly at 1 second by timestamp',
                'position': 1000.0,  # milliseconds
                'frame_data': 'dummy data by timestamp #3',
            },
            {
                'description': 'Get frame at some very high timestamp ',
                'position': sys.float_info.max,  # milliseconds
                'frame_data': 'dummy data by timestamp #4',
            },
        )

        for case in cases:
            with self.subTest(case['description']):
                video_mock = video_capture_mock(self.__class__.VIDEO_FILE_PATH)
                video_mock.read.return_value = (True, case['frame_data'])
                video_capture_mock.reset_mock()

                if isinstance(case['position'], int):
                    position_mock = frame_based_position_mock
                else:
                    position_mock = time_based_position_mock

                expected_video_capture_mock_calls = [
                    call(self.__class__.VIDEO_FILE_PATH),
                    call().set(position_mock, case['position']),
                    call().read(),
                    call().release(),
                ]

                expected_video_mock_calls = [
                    call.set(position_mock, case['position']),
                    call.read(),
                    call.release(),
                ]

                self.assertListEqual(video_capture_mock.mock_calls, [])
                self.assertListEqual(video_mock.mock_calls, [])

                self.assertEqual(
                    video.Video(self.__class__.VIDEO_FILE_PATH).get_frame(case['position']),
                    case['frame_data']
                )

                self.assertListEqual(video_capture_mock.mock_calls, expected_video_capture_mock_calls)
                self.assertListEqual(video_mock.mock_calls, expected_video_mock_calls)

    @patch('cv2.VideoCapture', spec=cv2.VideoCapture)
    def test_get_frame_with_wrong_types(self, video_capture_mock: Mock) -> None:
        wrong_type_inputs = [
            None,
            1j,
            '',
            '0',
            'foo',
            b'',
            b'0',
            b'foo',
            (0).to_bytes(length=1, byteorder=sys.byteorder),
            [],
            [0],
            ['foo'],
            ['foo', 'bar'],
            (),
            (0,),
            ('foo',),
            ('foo', 'bar'),
            dict(),
            {0: 'foo'},
            {'foo': 'bar'},
            set(),
            {0},
            {'foo'},
            {'foo', 'bar'},
        ]

        for wrong_type_input in wrong_type_inputs:
            with self.subTest(wrong_type_input):
                video_mock = video_capture_mock(self.__class__.VIDEO_FILE_PATH)
                video_capture_mock.reset_mock()

                expected_video_capture_mock_calls = [
                    call(self.__class__.VIDEO_FILE_PATH),
                    call().release(),
                ]
                expected_video_mock_calls = [
                    call.release(),
                ]

                self.assertListEqual(video_capture_mock.mock_calls, [])
                self.assertListEqual(video_mock.mock_calls, [])

                wrong_type = type(wrong_type_input)

                self.assertRaisesRegex(
                    TypeError,
                    (
                        r"^Argument 'position' must be of type '<class 'int'>' or '<class 'float'>', "
                        r"but '{}' was provided instead\.$"
                    ).format(wrong_type),
                    video.Video(self.__class__.VIDEO_FILE_PATH).get_frame,
                    wrong_type_input
                )

                self.assertListEqual(video_capture_mock.mock_calls, expected_video_capture_mock_calls)
                self.assertListEqual(video_mock.mock_calls, expected_video_mock_calls)

    @patch('cv2.VideoCapture', spec=cv2.VideoCapture)
    def test_get_frame_with_negative_numbers(self, video_capture_mock: Mock) -> None:
        negative_numbers = [
            -1,
            -2,
            -1000,
            -1 * int(sys.float_info.max),
            -0.1,
            -1.0,
            -1 * sys.float_info.epsilon,
            -1 * sys.float_info.min,
            -1 * sys.float_info.max,
            float('-inf'),
        ]

        for negative_number in negative_numbers:
            with self.subTest(negative_number):
                video_mock = video_capture_mock(self.__class__.VIDEO_FILE_PATH)
                video_capture_mock.reset_mock()

                expected_video_capture_mock_calls = [
                    call(self.__class__.VIDEO_FILE_PATH),
                    call().release(),
                ]
                expected_video_mock_calls = [
                    call.release()
                ]

                self.assertListEqual(video_capture_mock.mock_calls, [])
                self.assertListEqual(video_mock.mock_calls, [])

                self.assertRaisesRegex(
                    ValueError,
                    (
                        r"^Value of argument 'position' must be a non-negative number, "
                        r"but {} was provided instead\.$"
                    ).format(re.escape(str(negative_number))),
                    video.Video(self.__class__.VIDEO_FILE_PATH).get_frame,
                    negative_number
                )

                self.assertListEqual(video_capture_mock.mock_calls, expected_video_capture_mock_calls)
                self.assertListEqual(video_mock.mock_calls, expected_video_mock_calls)

    @patch('cv2.CAP_PROP_POS_FRAMES')
    @patch('cv2.CAP_PROP_POS_MSEC')
    @patch('cv2.VideoCapture', spec=cv2.VideoCapture)
    def test_get_frame_when_read_fails(
        self,
        video_capture_mock: Mock,
        time_based_position_mock: Mock,
        frame_based_position_mock: Mock
    ) -> None:

        cases = (
            {
                'description': 'Get frame by index',
                'position': 0,
                'frame_data': 'dummy data #1',
            },
            {
                'description': 'Get frame by timestamp',
                'position': 0.0,  # milliseconds
                'frame_data': 'dummy data #2',
            },
        )

        for case in cases:
            with self.subTest(case['description']):
                video_mock = video_capture_mock(self.__class__.VIDEO_FILE_PATH)
                video_mock.read.return_value = (False, case['frame_data'])
                video_capture_mock.reset_mock()

                if isinstance(case['position'], int):
                    position_mock = frame_based_position_mock
                else:
                    position_mock = time_based_position_mock

                expected_video_capture_mock_calls = [
                    call(self.__class__.VIDEO_FILE_PATH),
                    call().set(position_mock, case['position']),
                    call().read(),
                    call().release(),
                ]
                expected_video_mock_calls = [
                    call.set(position_mock, case['position']),
                    call.read(),
                    call.release(),
                ]

                self.assertListEqual(video_capture_mock.mock_calls, [])
                self.assertListEqual(video_mock.mock_calls, [])

                self.assertRaisesRegex(
                    RuntimeError,
                    r"^Unable to read video frame\.$",
                    video.Video(self.__class__.VIDEO_FILE_PATH).get_frame,
                    case['position']
                )

                self.assertListEqual(video_capture_mock.mock_calls, expected_video_capture_mock_calls)
                self.assertListEqual(video_mock.mock_calls, expected_video_mock_calls)
