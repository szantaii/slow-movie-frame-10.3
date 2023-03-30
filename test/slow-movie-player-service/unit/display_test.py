from module_helper import get_module_from_file
from unittest import TestCase
from unittest.mock import call, Mock, patch
import re
import subprocess
import signal
from typing import Any

processinfo = get_module_from_file('../../src/slow-movie-player-service/processinfo.py')
display = get_module_from_file('../../src/slow-movie-player-service/display.py')


class DisplayTest(TestCase):
    TEST_VCOM_VALUE = -1.48
    TEST_PATH_TO_IMAGE_FILE = '/path/to/image/file'

    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_clear(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock
    ) -> None:
        popen_command = [
            display.Display.UPDATE_DISPLAY_PATH,
            '-v',
            str(self.__class__.TEST_VCOM_VALUE)
        ]

        update_display_process_mock = popen_mock(
            popen_command,
            stdout=stdout_mock,
            stderr=stderr_mock,
            text=True
        )
        update_display_process_mock.returncode = 0
        update_display_process_mock.communicate.return_value = 'dummy output', None

        popen_mock.reset_mock()

        self.assertListEqual(popen_mock.mock_calls, [])
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(update_display_process_mock.mock_calls, [])

        try:
            display.Display.clear(self.__class__.TEST_VCOM_VALUE)
        except Exception as exception:
            self.fail('An exception was raised unexpectedly: {}'.format(exception))

        self.assertListEqual(
            popen_mock.mock_calls,
            [
                call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                call().communicate(timeout=display.Display.TIMEOUT),
            ]
        )
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(
            update_display_process_mock.mock_calls,
            [
                call.communicate(timeout=display.Display.TIMEOUT),
            ]
        )

    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_clear_with_non_zero_exit_status(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock
    ) -> None:
        popen_command = [
            display.Display.UPDATE_DISPLAY_PATH,
            '-v',
            str(self.__class__.TEST_VCOM_VALUE)
        ]

        cases: list[dict[str, Any]] = [
            {
                'description': 'No process output',
                'update_display_process_output': '',
                'update_display_process_exit_status': 999,
                'expected_exception_message_regex': r"^Error during updating display \(999\)\.$",
            },
            {
                'description': 'With output',
                'update_display_process_output': 'dummy process output',
                'update_display_process_exit_status': -2,
                'expected_exception_message_regex': r"^Error during updating display \(-2\): 'dummy process output'\.$",
            },
        ]

        for case in cases:
            with self.subTest(case['description']):

                update_display_process_mock = popen_mock(
                    popen_command,
                    stdout=stdout_mock,
                    stderr=stderr_mock,
                    text=True
                )
                update_display_process_mock.returncode = case['update_display_process_exit_status']
                update_display_process_mock.communicate.return_value = case['update_display_process_output'], None

                popen_mock.reset_mock()

                self.assertListEqual(popen_mock.mock_calls, [])
                self.assertListEqual(stdout_mock.mock_calls, [])
                self.assertListEqual(stderr_mock.mock_calls, [])
                self.assertListEqual(update_display_process_mock.mock_calls, [])

                self.assertRaisesRegex(
                    RuntimeError,
                    case['expected_exception_message_regex'],
                    display.Display.clear,
                    self.__class__.TEST_VCOM_VALUE
                )

                self.assertListEqual(
                    popen_mock.mock_calls,
                    [
                        call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                        call().communicate(timeout=display.Display.TIMEOUT),
                    ]
                )
                self.assertListEqual(stdout_mock.mock_calls, [])
                self.assertListEqual(stderr_mock.mock_calls, [])
                self.assertListEqual(
                    update_display_process_mock.mock_calls,
                    [
                        call.communicate(timeout=display.Display.TIMEOUT),
                    ]
                )

    @patch('processinfo.ProcessInfo.get_process_info', spec=processinfo.ProcessInfo.get_process_info)
    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_clear_with_process_timeout(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock,
        get_process_info_function_mock: Mock
    ) -> None:
        popen_command = [
            display.Display.UPDATE_DISPLAY_PATH,
            '-v',
            str(self.__class__.TEST_VCOM_VALUE)
        ]
        update_display_process_output = 'dummy process output'
        update_display_process_mock = popen_mock(
            popen_command,
            stdout=stdout_mock,
            stderr=stderr_mock,
            text=True
        )
        process_info_output = 'dummy process info output'
        get_process_info_function_mock.return_value = process_info_output

        cases: list[dict[str, Any]] = [
            {
                'description': 'No process output',
                'update_display_process_output': None,
                'expected_exception_message_regex': (
                    r"^Timeout during updating display\.\n"
                    r"Process info:\n"
                    r"{}$".format(re.escape(process_info_output))
                ),
            },
            {
                'description': 'With output',
                'update_display_process_output': update_display_process_output,
                'expected_exception_message_regex': (
                    r"^Timeout during updating display\.\n"
                    r"Process output: '{}'.\n"
                    r"Process info:\n"
                    r"{}$"
                ).format(
                    re.escape(update_display_process_output),
                    re.escape(process_info_output)
                ),
            }
        ]

        for case in cases:
            with self.subTest(case['description']):
                update_display_process_mock.communicate.side_effect = [
                    subprocess.TimeoutExpired(
                        popen_command,
                        display.Display.TIMEOUT,
                        case['update_display_process_output']
                    ),
                    (case['update_display_process_output'], None)
                ]

                popen_mock.reset_mock()
                update_display_process_mock.reset_mock()
                get_process_info_function_mock.reset_mock()

                self.assertListEqual(popen_mock.mock_calls, [])
                self.assertListEqual(stdout_mock.mock_calls, [])
                self.assertListEqual(stderr_mock.mock_calls, [])
                self.assertListEqual(update_display_process_mock.mock_calls, [])
                self.assertListEqual(get_process_info_function_mock.mock_calls, [])

                self.assertRaisesRegex(
                    RuntimeError,
                    case['expected_exception_message_regex'],
                    display.Display.clear,
                    self.__class__.TEST_VCOM_VALUE
                )

                self.assertListEqual(
                    popen_mock.mock_calls,
                    [
                        call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                        call().communicate(timeout=display.Display.TIMEOUT),
                        call().kill(),
                        call().communicate(),
                    ]
                )
                self.assertListEqual(stdout_mock.mock_calls, [])
                self.assertListEqual(stderr_mock.mock_calls, [])
                self.assertListEqual(
                    update_display_process_mock.mock_calls,
                    [
                        call.communicate(timeout=display.Display.TIMEOUT),
                        call.kill(),
                        call.communicate(),
                    ]
                )
                self.assertListEqual(
                    get_process_info_function_mock.mock_calls,
                    [
                        call(update_display_process_mock),
                    ]
                )

    @patch('signal.SIGUSR1')
    @patch('signal.SIGTERM')
    @patch('signal.sigtimedwait', spec=signal.sigtimedwait)
    @patch('signal.getsignal', spec=signal.getsignal)
    @patch('signal.signal', spec=signal.signal)
    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_update(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock,
        signal_function_mock: Mock,
        getsignal_function_mock: Mock,
        sigtimedwait_function_mock: Mock,
        sigterm_mock: Mock,
        sigusr1_mock: Mock
    ) -> None:
        popen_command = [
            display.Display.UPDATE_DISPLAY_PATH,
            '-d',
            '-v',
            str(self.__class__.TEST_VCOM_VALUE),
            '-f',
            self.__class__.TEST_PATH_TO_IMAGE_FILE
        ]

        update_display_process_mock = popen_mock(
            popen_command,
            stdout=stdout_mock,
            stderr=stderr_mock,
            text=True
        )
        update_display_process_mock.returncode = 0
        update_display_process_mock.communicate.return_value = 'dummy output', None

        popen_mock.reset_mock()

        self.assertListEqual(popen_mock.mock_calls, [])
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(signal_function_mock.mock_calls, [])
        self.assertListEqual(getsignal_function_mock.mock_calls, [])
        self.assertListEqual(sigtimedwait_function_mock.mock_calls, [])
        self.assertListEqual(sigterm_mock.mock_calls, [])
        self.assertListEqual(sigusr1_mock.mock_calls, [])
        self.assertListEqual(update_display_process_mock.mock_calls, [])

        with display.Display(self.__class__.TEST_VCOM_VALUE, self.__class__.TEST_PATH_TO_IMAGE_FILE) as dsp:
            self.assertListEqual(popen_mock.mock_calls, [])
            self.assertListEqual(stdout_mock.mock_calls, [])
            self.assertListEqual(stderr_mock.mock_calls, [])
            self.assertListEqual(signal_function_mock.mock_calls, [])
            self.assertListEqual(
                getsignal_function_mock.mock_calls,
                [
                    call(sigterm_mock),  # Save original SIGTERM signal handler in __init__
                ]
            )
            self.assertListEqual(sigtimedwait_function_mock.mock_calls, [])
            self.assertListEqual(sigterm_mock.mock_calls, [])
            self.assertListEqual(sigusr1_mock.mock_calls, [])
            self.assertListEqual(update_display_process_mock.mock_calls, [])

            dsp.update()

            self.assertListEqual(
                popen_mock.mock_calls,
                [
                    call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),  # Start update-display
                    call().send_signal(sigusr1_mock),  # Send SIGUSR1 to update-display to draw image on screen
                ]
            )
            self.assertListEqual(stdout_mock.mock_calls, [])
            self.assertListEqual(stderr_mock.mock_calls, [])
            self.assertListEqual(
                signal_function_mock.mock_calls,
                [
                    call(sigterm_mock, dsp._Display__sigterm_handler),  # Set SIGTERM handler function in __start
                    call(sigusr1_mock, display.Display._Display__noop_signal_handler),  # Set SIGUSR1 handler function in __start
                ]
            )
            self.assertListEqual(getsignal_function_mock.mock_calls, [call(sigterm_mock)])
            self.assertListEqual(
                sigtimedwait_function_mock.mock_calls,
                [
                    call([sigusr1_mock], display.Display.TIMEOUT),  # Wait for update-display to get ready
                    call([sigusr1_mock], display.Display.TIMEOUT),  # Wait until image was drawn on display
                ]
            )
            self.assertListEqual(sigterm_mock.mock_calls, [])
            self.assertListEqual(sigusr1_mock.mock_calls, [])
            self.assertListEqual(
                update_display_process_mock.mock_calls,
                [
                    call.send_signal(sigusr1_mock),  # Send SIGUSR1 to update-display to draw image on screen
                ]
            )

            dsp.update()

            self.assertListEqual(
                popen_mock.mock_calls,
                [
                    call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                    call().send_signal(sigusr1_mock),
                    call().send_signal(sigusr1_mock),  # Send SIGUSR1 to update-display to draw image on screen again
                ]
            )
            self.assertListEqual(stdout_mock.mock_calls, [])
            self.assertListEqual(stderr_mock.mock_calls, [])
            self.assertListEqual(
                signal_function_mock.mock_calls,
                [
                    call(sigterm_mock, dsp._Display__sigterm_handler),
                    call(sigusr1_mock, dsp._Display__noop_signal_handler),
                ]
            )
            self.assertListEqual(
                getsignal_function_mock.mock_calls,
                [
                    call(sigterm_mock),
                ]
            )
            self.assertListEqual(
                sigtimedwait_function_mock.mock_calls,
                [
                    call([sigusr1_mock], display.Display.TIMEOUT),
                    call([sigusr1_mock], display.Display.TIMEOUT),
                    call([sigusr1_mock], display.Display.TIMEOUT),  # Wait until image was drawn on display again
                ]
            )
            self.assertListEqual(sigterm_mock.mock_calls, [])
            self.assertListEqual(sigusr1_mock.mock_calls, [])
            self.assertListEqual(
                update_display_process_mock.mock_calls,
                [
                    call.send_signal(sigusr1_mock),
                    call.send_signal(sigusr1_mock),  # Send SIGUSR1 to update-display to draw image on screen again
                ]
            )

        self.assertListEqual(
            popen_mock.mock_calls,
            [
                call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                call().send_signal(sigusr1_mock),
                call().send_signal(sigusr1_mock),
                call().send_signal(sigterm_mock),  # Send SIGTERM to update-display to stop
                call().communicate(timeout=display.Display.TIMEOUT),  # Wait for update-display to stop, etc.
            ]
        )
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(
            signal_function_mock.mock_calls,
            [
                call(sigterm_mock, dsp._Display__sigterm_handler),
                call(sigusr1_mock, dsp._Display__noop_signal_handler),
            ]
        )
        self.assertListEqual(
            getsignal_function_mock.mock_calls,
            [
                call(sigterm_mock),
            ]
        )
        self.assertListEqual(
            sigtimedwait_function_mock.mock_calls,
            [
                call([sigusr1_mock], display.Display.TIMEOUT),
                call([sigusr1_mock], display.Display.TIMEOUT),
                call([sigusr1_mock], display.Display.TIMEOUT),
            ]
        )
        self.assertListEqual(sigterm_mock.mock_calls, [])
        self.assertListEqual(sigusr1_mock.mock_calls, [])
        self.assertListEqual(
            update_display_process_mock.mock_calls,
            [
                call.send_signal(sigusr1_mock),
                call.send_signal(sigusr1_mock),
                call.send_signal(sigterm_mock),  # Send SIGTERM to update-display to stop
                call.communicate(timeout=display.Display.TIMEOUT),  # Wait for update-display to stop, etc.
            ]
        )

    @patch('signal.SIGUSR1')
    @patch('signal.SIGTERM')
    @patch('signal.raise_signal', spec=signal.raise_signal)
    @patch('signal.sigtimedwait', spec=signal.sigtimedwait)
    @patch('signal.getsignal', spec=signal.getsignal)
    @patch('signal.signal', spec=signal.signal)
    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_sigterm_handling(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock,
        signal_function_mock: Mock,
        getsignal_function_mock: Mock,
        sigtimedwait_function_mock: Mock,
        raise_signal_function_mock: Mock,
        sigterm_mock: Mock,
        sigusr1_mock: Mock
    ) -> None:

        popen_command = [
            display.Display.UPDATE_DISPLAY_PATH,
            '-d',
            '-v',
            str(self.__class__.TEST_VCOM_VALUE),
            '-f',
            self.__class__.TEST_PATH_TO_IMAGE_FILE
        ]

        update_display_process_mock = popen_mock(
            popen_command,
            stdout=stdout_mock,
            stderr=stderr_mock,
            text=True
        )
        update_display_process_mock.returncode = 0
        update_display_process_mock.communicate.return_value = None, None

        original_sigterm_handler_mock = getsignal_function_mock(sigterm_mock)

        popen_mock.reset_mock()
        getsignal_function_mock.reset_mock()

        self.assertListEqual(popen_mock.mock_calls, [])
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(signal_function_mock.mock_calls, [])
        self.assertListEqual(getsignal_function_mock.mock_calls, [])
        self.assertListEqual(sigtimedwait_function_mock.mock_calls, [])
        self.assertListEqual(raise_signal_function_mock.mock_calls, [])
        self.assertListEqual(sigterm_mock.mock_calls, [])
        self.assertListEqual(sigusr1_mock.mock_calls, [])
        self.assertListEqual(update_display_process_mock.mock_calls, [])
        self.assertListEqual(original_sigterm_handler_mock.mock_calls, [])

        dsp = display.Display(self.__class__.TEST_VCOM_VALUE, self.__class__.TEST_PATH_TO_IMAGE_FILE)

        self.assertListEqual(popen_mock.mock_calls, [])
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(signal_function_mock.mock_calls, [])
        self.assertListEqual(
            getsignal_function_mock.mock_calls,
            [
                call(sigterm_mock),
            ]
        )
        self.assertListEqual(sigtimedwait_function_mock.mock_calls, [])
        self.assertListEqual(raise_signal_function_mock.mock_calls, [])
        self.assertListEqual(sigterm_mock.mock_calls, [])
        self.assertListEqual(sigusr1_mock.mock_calls, [])
        self.assertListEqual(update_display_process_mock.mock_calls, [])
        self.assertListEqual(original_sigterm_handler_mock.mock_calls, [])

        dsp.update()

        self.assertListEqual(
            popen_mock.mock_calls,
            [
                call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                call().send_signal(sigusr1_mock),
            ]
        )
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(
            signal_function_mock.mock_calls,
            [
                call(sigterm_mock, dsp._Display__sigterm_handler),
                call(sigusr1_mock, display.Display._Display__noop_signal_handler),
            ]
        )
        self.assertListEqual(
            getsignal_function_mock.mock_calls,
            [
                call(sigterm_mock),
            ]
        )
        self.assertListEqual(
            sigtimedwait_function_mock.mock_calls,
            [
                call([sigusr1_mock], display.Display.TIMEOUT),
                call([sigusr1_mock], display.Display.TIMEOUT),
            ]
        )
        self.assertListEqual(raise_signal_function_mock.mock_calls, [])
        self.assertListEqual(sigterm_mock.mock_calls, [])
        self.assertListEqual(sigusr1_mock.mock_calls, [])
        self.assertListEqual(
            update_display_process_mock.mock_calls,
            [
                call.send_signal(sigusr1_mock),
            ]
        )
        self.assertListEqual(original_sigterm_handler_mock.mock_calls, [])

        # Manually call Display's SIGTERM handler (not nice, but it gets the work done)
        dsp._Display__sigterm_handler()

        self.assertListEqual(
            popen_mock.mock_calls,
            [
                call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                call().send_signal(sigusr1_mock),
                call().send_signal(sigterm_mock),  # Send SIGTERM to update-display to stop
                call().communicate(timeout=display.Display.TIMEOUT),  # Wait for update-display to stop, etc.
            ]
        )
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(
            signal_function_mock.mock_calls,
            [
                call(sigterm_mock, dsp._Display__sigterm_handler),
                call(sigusr1_mock, display.Display._Display__noop_signal_handler),
                call(sigterm_mock, original_sigterm_handler_mock),  # Reset back to the original SIGTERM handler after stopping update-display
            ]
        )
        self.assertListEqual(
            getsignal_function_mock.mock_calls,
            [
                call(sigterm_mock),
            ]
        )
        self.assertListEqual(
            sigtimedwait_function_mock.mock_calls,
            [
                call([sigusr1_mock], display.Display.TIMEOUT),
                call([sigusr1_mock], display.Display.TIMEOUT),
            ]
        )
        self.assertListEqual(
            raise_signal_function_mock.mock_calls,
            [
                call(sigterm_mock),  # Raise SIGTERM to propagate shutdown for the rest
            ]
        )
        self.assertListEqual(sigterm_mock.mock_calls, [])
        self.assertListEqual(sigusr1_mock.mock_calls, [])
        self.assertListEqual(
            update_display_process_mock.mock_calls,
            [
                call.send_signal(sigusr1_mock),
                call.send_signal(sigterm_mock),  # Send SIGTERM to update-display to stop
                call.communicate(timeout=display.Display.TIMEOUT),  # Wait for update-display to stop, etc.
            ]
        )
        self.assertListEqual(original_sigterm_handler_mock.mock_calls, [])

    @patch('signal.sigtimedwait', spec=signal.sigtimedwait)
    @patch('signal.getsignal', spec=signal.getsignal)
    @patch('signal.signal', spec=signal.signal)
    @patch('signal.SIGTERM')
    @patch('signal.SIGUSR1')
    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_update_with_non_zero_exit_status(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock,
        sigusr1_mock: Mock,
        sigterm_mock: Mock,
        *_: Mock
    ) -> None:
        popen_command = [
            display.Display.UPDATE_DISPLAY_PATH,
            '-d',
            '-v',
            str(self.__class__.TEST_VCOM_VALUE),
            '-f',
            self.__class__.TEST_PATH_TO_IMAGE_FILE
        ]

        cases: list[dict[str, Any]] = [
            {
                'description': 'No process output',
                'update_display_process_output': None,
                'update_display_process_exit_status': 1,
                'expected_exception_message': 'Error during updating display (1).',
            },
            {
                'description': 'With output',
                'update_display_process_output': 'dummy process output',
                'update_display_process_exit_status': -1,
                'expected_exception_message': "Error during updating display (-1): 'dummy process output'.",
            },
        ]

        for case in cases:
            with self.subTest(case['description']):
                update_display_process_mock = popen_mock(
                    popen_command,
                    stdout=stdout_mock,
                    stderr=stderr_mock,
                    text=True
                )
                update_display_process_mock.returncode = case['update_display_process_exit_status']
                update_display_process_mock.communicate.return_value = case['update_display_process_output'], None

                popen_mock.reset_mock()

                self.assertListEqual(popen_mock.mock_calls, [])
                self.assertListEqual(stdout_mock.mock_calls, [])
                self.assertListEqual(stderr_mock.mock_calls, [])
                self.assertListEqual(update_display_process_mock.mock_calls, [])

                try:
                    with display.Display(self.__class__.TEST_VCOM_VALUE, self.__class__.TEST_PATH_TO_IMAGE_FILE) as dsp:

                        self.assertListEqual(popen_mock.mock_calls, [])
                        self.assertListEqual(stdout_mock.mock_calls, [])
                        self.assertListEqual(stderr_mock.mock_calls, [])
                        self.assertListEqual(update_display_process_mock.mock_calls, [])

                        dsp.update()

                        self.assertListEqual(
                            popen_mock.mock_calls,
                            [
                                call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                                call().send_signal(sigusr1_mock),
                            ]
                        )
                        self.assertListEqual(stdout_mock.mock_calls, [])
                        self.assertListEqual(stderr_mock.mock_calls, [])
                        self.assertListEqual(
                            update_display_process_mock.mock_calls,
                            [
                                call.send_signal(sigusr1_mock),
                            ]
                        )

                except RuntimeError as error:
                    self.assertEqual(
                        case['expected_exception_message'],
                        str(error)
                    )

                    self.assertListEqual(
                        popen_mock.mock_calls,
                        [
                            call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                            call().send_signal(sigusr1_mock),
                            call().send_signal(sigterm_mock),
                            call().communicate(timeout=display.Display.TIMEOUT),
                        ]
                    )
                    self.assertListEqual(stdout_mock.mock_calls, [])
                    self.assertListEqual(stderr_mock.mock_calls, [])
                    self.assertListEqual(
                        update_display_process_mock.mock_calls,
                        [
                            call.send_signal(sigusr1_mock),
                            call.send_signal(sigterm_mock),
                            call.communicate(timeout=display.Display.TIMEOUT),
                        ]
                    )

                    continue

                self.fail('The expected exception was not raised.')

    @patch('signal.sigtimedwait', spec=signal.sigtimedwait)
    @patch('signal.getsignal', spec=signal.getsignal)
    @patch('signal.signal', spec=signal.signal)
    @patch('signal.SIGTERM')
    @patch('signal.SIGUSR1')
    @patch('processinfo.ProcessInfo.get_process_info', spec=processinfo.ProcessInfo.get_process_info)
    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_update_with_process_timeout(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock,
        get_process_info_function_mock: Mock,
        sigusr1_mock: Mock,
        sigterm_mock: Mock,
        *_: Mock
    ) -> None:
        popen_command = [
            display.Display.UPDATE_DISPLAY_PATH,
            '-d',
            '-v',
            str(self.__class__.TEST_VCOM_VALUE),
            '-f',
            self.__class__.TEST_PATH_TO_IMAGE_FILE
        ]
        update_display_process_output = 'dummy process output'
        update_display_process_mock = popen_mock(
            popen_command,
            stdout=stdout_mock,
            stderr=stderr_mock,
            text=True
        )
        process_info_output = 'dummy process info output'
        get_process_info_function_mock.return_value = process_info_output

        cases: list[dict[str, Any]] = [
            {
                'description': 'No output',
                'update_display_process_output': None,
                'expected_exception_message': (
                    'Timeout during updating display.\n'
                    'Process info:\n{}'
                ).format(
                    process_info_output
                ),
            },
            {
                'description': 'With output',
                'update_display_process_output': update_display_process_output,
                'expected_exception_message': (
                    'Timeout during updating display.\n'
                    "Process output: '{}'.\n"
                    'Process info:\n{}'
                ).format(
                    update_display_process_output,
                    process_info_output
                ),
            },
        ]

        for case in cases:
            with self.subTest(case['description']):
                update_display_process_mock.communicate.side_effect = [
                    subprocess.TimeoutExpired(
                        popen_command,
                        display.Display.TIMEOUT,
                        case['update_display_process_output']
                    ),
                    (case['update_display_process_output'], None)
                ]

                popen_mock.reset_mock()
                get_process_info_function_mock.reset_mock()
                update_display_process_mock.reset_mock()

                self.assertListEqual(popen_mock.mock_calls, [])
                self.assertListEqual(stdout_mock.mock_calls, [])
                self.assertListEqual(stderr_mock.mock_calls, [])
                self.assertListEqual(update_display_process_mock.mock_calls, [])
                self.assertListEqual(get_process_info_function_mock.mock_calls, [])

                try:
                    with display.Display(self.__class__.TEST_VCOM_VALUE, self.__class__.TEST_PATH_TO_IMAGE_FILE) as dsp:
                        self.assertListEqual(popen_mock.mock_calls, [])
                        self.assertListEqual(stdout_mock.mock_calls, [])
                        self.assertListEqual(stderr_mock.mock_calls, [])
                        self.assertListEqual(update_display_process_mock.mock_calls, [])
                        self.assertListEqual(get_process_info_function_mock.mock_calls, [])

                        dsp.update()

                        self.assertListEqual(
                            popen_mock.mock_calls,
                            [
                                call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                                call().send_signal(sigusr1_mock),
                            ]
                        )
                        self.assertListEqual(stdout_mock.mock_calls, [])
                        self.assertListEqual(stderr_mock.mock_calls, [])
                        self.assertListEqual(
                            update_display_process_mock.mock_calls,
                            [
                                call.send_signal(sigusr1_mock),
                            ]
                        )
                        self.assertListEqual(get_process_info_function_mock.mock_calls, [])

                except RuntimeError as error:
                    self.assertEqual(
                        case['expected_exception_message'],
                        str(error)
                    )

                    self.assertListEqual(
                        popen_mock.mock_calls,
                        [
                            call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                            call().send_signal(sigusr1_mock),
                            call().send_signal(sigterm_mock),
                            call().communicate(timeout=display.Display.TIMEOUT),
                            call().kill(),
                            call().communicate(),
                        ]
                    )
                    self.assertListEqual(stdout_mock.mock_calls, [])
                    self.assertListEqual(stderr_mock.mock_calls, [])
                    self.assertListEqual(
                        update_display_process_mock.mock_calls,
                        [
                            call.send_signal(sigusr1_mock),
                            call.send_signal(sigterm_mock),
                            call.communicate(timeout=display.Display.TIMEOUT),
                            call.kill(),
                            call.communicate(),
                        ]
                    )
                    self.assertListEqual(
                        get_process_info_function_mock.mock_calls,
                        [call(update_display_process_mock)]
                    )

                    continue

                self.fail('The expected exception was not raised.')
