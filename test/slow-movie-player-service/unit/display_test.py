from module_helper import get_module_from_file
from unittest import TestCase
from unittest.mock import call, Mock, patch
import re
import subprocess
from typing import Any

processinfo = get_module_from_file('../../src/slow-movie-player-service/processinfo.py')
display = get_module_from_file('../../src/slow-movie-player-service/display.py')


class DisplayTest(TestCase):
    TEST_VCOM_VALUE = -1.48
    TEST_PATH_TO_IMAGE_FILE = '/path/to/image/file'

    @patch('display.ProcessInfo', spec=processinfo.ProcessInfo)
    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_clear(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock,
        process_info_mock: Mock
    ) -> None:
        self.do_test_with_mocks(
            popen_mock,
            stdout_mock,
            stderr_mock,
            process_info_mock,
            popen_command=['/opt/slow-movie-player/update-display', '-v', str(self.__class__.TEST_VCOM_VALUE)],
            process_timeout=None,
            process_output='dummy output, does not really matter',
            process_exit_status=0,
            test_function=display.Display.clear,
            test_function_args=[self.__class__.TEST_VCOM_VALUE]
        )

    @patch('display.ProcessInfo', spec=processinfo.ProcessInfo)
    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_clear_with_non_zero_subprocess_exit_status(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock,
        process_info_mock: Mock
    ) -> None:

        self.do_test_with_mocks(
            popen_mock,
            stdout_mock,
            stderr_mock,
            process_info_mock,
            popen_command=['/opt/slow-movie-player/update-display', '-v', str(self.__class__.TEST_VCOM_VALUE)],
            process_timeout=None,
            process_output='this should be included in the exception message',
            process_exit_status=-1,
            test_function=display.Display.clear,
            test_function_args=[self.__class__.TEST_VCOM_VALUE]
        )

    @patch('display.ProcessInfo', spec=processinfo.ProcessInfo)
    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_draw_image(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock,
        process_info_mock: Mock
    ) -> None:
        self.do_test_with_mocks(
            popen_mock,
            stdout_mock,
            stderr_mock,
            process_info_mock,
            popen_command=[
                '/opt/slow-movie-player/update-display',
                '-v',
                str(self.__class__.TEST_VCOM_VALUE),
                '-f',
                self.__class__.TEST_PATH_TO_IMAGE_FILE
            ],
            process_output=None,
            process_timeout=60,
            process_exit_status=0,
            test_function=display.Display.draw_image,
            test_function_args=[
                self.__class__.TEST_VCOM_VALUE,
                self.__class__.TEST_PATH_TO_IMAGE_FILE
            ]
        )

    @patch('display.ProcessInfo', spec=processinfo.ProcessInfo)
    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_draw_image_with_non_zero_subprocess_exit_status(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock,
        process_info_mock: Mock
    ) -> None:

        self.do_test_with_mocks(
            popen_mock,
            stdout_mock,
            stderr_mock,
            process_info_mock,
            popen_command=[
                '/opt/slow-movie-player/update-display',
                '-v',
                str(self.__class__.TEST_VCOM_VALUE),
                '-f',
                self.__class__.TEST_PATH_TO_IMAGE_FILE
            ],
            process_timeout=60,
            process_output='this is included in the expected exception message',
            process_exit_status=1,
            test_function=display.Display.draw_image,
            test_function_args=[
                self.__class__.TEST_VCOM_VALUE,
                self.__class__.TEST_PATH_TO_IMAGE_FILE
            ]
        )

    def do_test_with_mocks(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock,
        process_info_mock: Mock,
        **kwargs
    ) -> None:
        process_mock = popen_mock(kwargs['popen_command'], stdout=stdout_mock, stderr=stderr_mock, text=True)
        process_mock.communicate.return_value = kwargs['process_output'], None
        process_mock.returncode = kwargs['process_exit_status']
        popen_mock.reset_mock()

        expected_popen_mock_calls = [
            call(kwargs['popen_command'], stdout=stdout_mock, stderr=stderr_mock, text=True),
            call().communicate(timeout=kwargs['process_timeout']),
        ]
        expected_process_mock_calls = [
            call.communicate(timeout=kwargs['process_timeout']),
        ]

        self.assertListEqual(popen_mock.mock_calls, [])
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(process_mock.mock_calls, [])
        self.assertListEqual(process_info_mock.mock_calls, [])

        if process_mock.returncode == 0:
            kwargs['test_function'](*kwargs['test_function_args'])
        else:
            self.assertRaisesRegex(
                RuntimeError,
                r"^Error during updating display \({}\): '{}'\.$".format(
                    kwargs['process_exit_status'],
                    re.escape(kwargs['process_output'])
                ),
                kwargs['test_function'],
                *kwargs['test_function_args']
            )

        self.assertListEqual(popen_mock.mock_calls, expected_popen_mock_calls)
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(process_mock.mock_calls, expected_process_mock_calls)
        self.assertListEqual(process_info_mock.mock_calls, [])

    @patch('display.ProcessInfo', spec=processinfo.ProcessInfo)
    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_draw_image_with_timeout_exception(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock,
        process_info_mock: Mock
    ) -> None:
        popen_command = [
            '/opt/slow-movie-player/update-display',
            '-v',
            str(self.__class__.TEST_VCOM_VALUE),
            '-f',
            self.__class__.TEST_PATH_TO_IMAGE_FILE
        ]

        cases: list[dict[str, Any]] = [
            {
                'description': 'Timeout expired #1',
                'process_exit_status': 0,
                'process_output': 'dummy output',
                'process_status': 'dummy process status',
                'stack_trace': 'dummy stack trace',
                'kernel_trace': 'dummy kernel trace',
            },
            {
                'description': 'Timeout expired #2',
                'process_exit_status': -1,
                'process_output': None,
                'process_status': 'dummy process status\n',
                'stack_trace': 'dummy stack trace\n',
                'kernel_trace': None,
            },
            {
                'description': 'Timeout expired #3',
                'process_exit_status': 111,
                'process_output': None,
                'process_status': 'dummy process status\n',
                'stack_trace': 'dummy stack trace',
                'kernel_trace': None,
            },
            {
                'description': 'Timeout expired #4',
                'process_exit_status': 222,
                'process_output': 'some dummy output here\n\n\n',
                'process_status': 'something...something',
                'stack_trace': 'nothing to see here',
                'kernel_trace': None,
            },
            {
                'description': 'Timeout expired #5',
                'process_exit_status': -273.15,
                'process_output': None,
                'process_status': 'Hello,',
                'stack_trace': 'World!',
                'kernel_trace': 'nothing to see here either...\n',
            },
        ]

        for case in cases:
            with self.subTest(case['description']):
                process_mock = popen_mock(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True)
                process_mock.returncode = case['process_exit_status']
                process_mock.communicate.return_value = case['process_output'], None
                process_mock.communicate.side_effect = [
                    subprocess.TimeoutExpired(popen_command, 60.0, case['process_output']),
                    (case['process_output'], None)
                ]
                process_mock.pid = 111

                process_info_mock.get_status.return_value = case['process_status']
                process_info_mock.get_stack_trace.return_value = case['stack_trace']
                process_info_mock.get_kernel_trace.return_value = case['kernel_trace']

                popen_mock.reset_mock()
                process_info_mock.reset_mock()

                expected_popen_mock_calls = [
                    call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                    call().communicate(timeout=60),
                    call().kill(),
                    call().communicate(),
                ]
                expected_process_mock_calls = [
                    call.communicate(timeout=60),
                    call.kill(),
                    call.communicate(),
                ]
                expected_process_info_mock_calls = [
                    call.get_status(process_mock.pid),
                    call.get_kernel_trace(process_mock.pid),
                    call.get_stack_trace(process_mock.pid),
                ]

                self.assertListEqual(popen_mock.mock_calls, [])
                self.assertListEqual(stdout_mock.mock_calls, [])
                self.assertListEqual(stderr_mock.mock_calls, [])
                self.assertListEqual(process_mock.mock_calls, [])

                self.assertRaisesRegex(
                    RuntimeError,
                    (
                        r"^Timeout during updating display\.\n"
                        r"--- Process status:\n{process_status}\n"
                        r"--- Stack trace:\n{stack_trace}"
                        r"{new_line}"
                        r"{kernel_trace}"
                        r"{process_output}"
                        r"$"
                    ).format(
                        process_status=re.escape(case['process_status'].rstrip('\n')),
                        stack_trace=re.escape(case['stack_trace'].rstrip('\n')),
                        new_line=(
                            '\n' if case['kernel_trace'] or case['process_output'] else ''
                        ),
                        kernel_trace=(
                            r"--- Kernel trace:\n{}\n".format(
                                re.escape(case['kernel_trace'].rstrip('\n'))
                            ) if case['kernel_trace'] else ''
                        ),
                        process_output=(
                            r"--- Output:\n{}".format(
                                re.escape(case['process_output'])
                            ) if case['process_output'] else ''
                        )
                    ),
                    display.Display.draw_image,
                    self.__class__.TEST_VCOM_VALUE,
                    self.__class__.TEST_PATH_TO_IMAGE_FILE
                )

                self.assertListEqual(popen_mock.mock_calls, expected_popen_mock_calls)
                self.assertListEqual(stdout_mock.mock_calls, [])
                self.assertListEqual(stderr_mock.mock_calls, [])
                self.assertListEqual(process_mock.mock_calls, expected_process_mock_calls)
                self.assertListEqual(process_info_mock.mock_calls, expected_process_info_mock_calls)
