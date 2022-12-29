from module_helper import get_module_from_file
from unittest import TestCase
from unittest.mock import call, Mock, patch
import subprocess

display = get_module_from_file('../../src/slow-movie-player-service/display.py')


class DisplayTest(TestCase):
    TEST_VCOM_VALUE = -1.48
    TEST_PATH_TO_IMAGE_FILE = '/path/to/image/file'

    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_clear(self, popen_mock: Mock, stdout_mock: Mock, stderr_mock: Mock) -> None:
        self.do_test_with_mocks(
            popen_mock,
            stdout_mock,
            stderr_mock,
            popen_command=['/opt/slow-movie-player/update-display', '-v', str(self.__class__.TEST_VCOM_VALUE)],
            process_output='dummy output, does not really matter',
            process_exit_status=0,
            test_function=display.Display.clear,
            test_function_args=[self.__class__.TEST_VCOM_VALUE]
        )

    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_clear_with_non_zero_subprocess_exit_status(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock
    ) -> None:

        self.do_test_with_mocks(
            popen_mock,
            stdout_mock,
            stderr_mock,
            popen_command=['/opt/slow-movie-player/update-display', '-v', str(self.__class__.TEST_VCOM_VALUE)],
            process_output='this should be included in the exception message',
            process_exit_status=-1,
            test_function=display.Display.clear,
            test_function_args=[self.__class__.TEST_VCOM_VALUE]
        )

    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_draw_image(self, popen_mock: Mock, stdout_mock: Mock, stderr_mock: Mock) -> None:
        self.do_test_with_mocks(
            popen_mock,
            stdout_mock,
            stderr_mock,
            popen_command=[
                '/opt/slow-movie-player/update-display',
                '-v',
                str(self.__class__.TEST_VCOM_VALUE),
                '-f',
                self.__class__.TEST_PATH_TO_IMAGE_FILE
            ],
            process_output=None,
            process_exit_status=0,
            test_function=display.Display.draw_image,
            test_function_args=[
                self.__class__.TEST_VCOM_VALUE,
                self.__class__.TEST_PATH_TO_IMAGE_FILE
            ]
        )

    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_draw_image_with_non_zero_subprocess_exit_status(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock
    ) -> None:

        self.do_test_with_mocks(
            popen_mock,
            stdout_mock,
            stderr_mock,
            popen_command=[
                '/opt/slow-movie-player/update-display',
                '-v',
                str(self.__class__.TEST_VCOM_VALUE),
                '-f',
                self.__class__.TEST_PATH_TO_IMAGE_FILE
            ],
            process_output='this is included in the expected exception message',
            process_exit_status=1,
            test_function=display.Display.draw_image,
            test_function_args=[
                self.__class__.TEST_VCOM_VALUE,
                self.__class__.TEST_PATH_TO_IMAGE_FILE
            ]
        )

    def do_test_with_mocks(self, popen_mock: Mock, stdout_mock: Mock, stderr_mock: Mock, **kwargs) -> None:
        process_mock = popen_mock(kwargs['popen_command'], stdout=stdout_mock, stderr=stderr_mock)
        process_mock.communicate.return_value = kwargs['process_output'], None
        process_mock.returncode = kwargs['process_exit_status']
        popen_mock.reset_mock()

        expected_popen_mock_calls = [
            call(kwargs['popen_command'], stdout=stdout_mock, stderr=stderr_mock),
            call().communicate(),
        ]
        expected_process_mock_calls = [
            call.communicate(),
        ]

        self.assertListEqual(popen_mock.mock_calls, [])
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(process_mock.mock_calls, [])

        if process_mock.returncode == 0:
            kwargs['test_function'](*kwargs['test_function_args'])
        else:
            self.assertRaisesRegex(
                RuntimeError,
                r"^Error during updating display: '{}'\.$".format(kwargs['process_output']),
                kwargs['test_function'],
                *kwargs['test_function_args']
            )

        self.assertListEqual(popen_mock.mock_calls, expected_popen_mock_calls)
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(process_mock.mock_calls, expected_process_mock_calls)
