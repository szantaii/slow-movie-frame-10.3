from module_helper import get_module_from_file
from unittest import TestCase
from unittest.mock import call, Mock, mock_open, patch
import os
import subprocess
from typing import Any

processinfo = get_module_from_file('../../src/slow-movie-player-service/processinfo.py')


class ProcessInfoTest(TestCase):
    def test_get_status(self) -> None:
        process_id = 123456789
        process_status = 'process status text'
        expected_process_status = process_status
        expected_open_function_mock_calls = [
            call('/proc/{}/status'.format(process_id), 'r'),
            call().__enter__(),
            call().read(),
            call().__exit__(None, None, None),
        ]

        with patch('builtins.open', mock_open(read_data=process_status)) as open_function_mock:
            actual_process_status = processinfo.ProcessInfo.get_status(process_id)

        self.assertEqual(actual_process_status, expected_process_status)
        self.assertListEqual(open_function_mock.mock_calls, expected_open_function_mock_calls)

    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    def test_get_stack_trace(
        self,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock
    ) -> None:
        stack_trace = 'imagine a stack trace here'
        process_id = 9876543210
        popen_command = [
            'gdb',
            '-ex', 'set pagination off',
            '-ex', 'attach {}'.format(process_id),
            '-ex', 'thread apply all bt full',
            '-ex', 'detach',
            '-ex', 'q'
        ]
        process_mock = popen_mock(
            popen_command,
            stdout=stdout_mock,
            stderr=stderr_mock,
            text=True
        )
        process_mock.communicate.return_value = stack_trace, None
        expected_popen_mock_calls = [
            call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
            call().communicate()
        ]
        expected_process_mock_calls = [
            call.communicate(),
        ]

        popen_mock.reset_mock()

        self.assertListEqual(popen_mock.mock_calls, [])
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(process_mock.mock_calls, [])

        self.assertEqual(processinfo.ProcessInfo.get_stack_trace(process_id), stack_trace)

        self.assertListEqual(popen_mock.mock_calls, expected_popen_mock_calls)
        self.assertListEqual(stdout_mock.mock_calls, [])
        self.assertListEqual(stderr_mock.mock_calls, [])
        self.assertListEqual(process_mock.mock_calls, expected_process_mock_calls)

    @patch('subprocess.STDOUT')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    @patch('os.path.exists', spec=os.path.exists)
    def test_get_kernel_trace(
        self,
        os_path_exists_function_mock: Mock,
        popen_mock: Mock,
        stdout_mock: Mock,
        stderr_mock: Mock
    ) -> None:
        kernel_config_file_path = '/proc/config.gz'

        cases: list[dict[str, Any]] = [
            {
                'description': 'Kernel config file does not exist',
                'process_id': 111,
                'kernel_config_file_exists': False,
            },
            {
                'description': 'Kernel not configured with stack backtrace support',
                'process_id': 222,
                'kernel_config_file_exists': True,
                'kernel_config_contents': '',
            },
            {
                'description': 'Kernel configured with stack backtrace support',
                'process_id': 333,
                'kernel_config_file_exists': True,
                'kernel_config_contents': (
                    'something-something\n'
                    'CONFIG_STACKTRACE=y\n'
                    'some other stuff here\n'
                ),
                'kernel_trace': 'dummy kernel trace',
            },
        ]

        expected_os_path_exists_function_mock_calls = [
            call(kernel_config_file_path)
        ]

        for case in cases:
            with self.subTest(case['description']):
                os_path_exists_function_mock.side_effect = {
                    kernel_config_file_path: case['kernel_config_file_exists']
                }.get

                os_path_exists_function_mock.reset_mock()
                popen_mock.reset_mock()

                self.assertListEqual(os_path_exists_function_mock.mock_calls, [])
                self.assertListEqual(popen_mock.mock_calls, [])
                self.assertListEqual(stdout_mock.mock_calls, [])
                self.assertListEqual(stderr_mock.mock_calls, [])

                if not case['kernel_config_file_exists']:
                    self.assertEqual(
                        processinfo.ProcessInfo.get_kernel_trace(case['process_id']),
                        None
                    )

                    self.assertListEqual(
                        os_path_exists_function_mock.mock_calls,
                        expected_os_path_exists_function_mock_calls
                    )
                    self.assertListEqual(popen_mock.mock_calls, [])
                    self.assertListEqual(stdout_mock.mock_calls, [])
                    self.assertListEqual(stderr_mock.mock_calls, [])

                    continue

                popen_command = ['zcat', kernel_config_file_path]
                process_mock = popen_mock(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True)
                process_mock.communicate.return_value = case['kernel_config_contents'], None
                expected_popen_mock_calls = [
                    call(popen_command, stdout=stdout_mock, stderr=stderr_mock, text=True),
                    call().communicate(),
                ]
                expected_process_mock_calls = [
                    call.communicate(),
                ]

                popen_mock.reset_mock()
                process_mock.reset_mock()

                self.assertListEqual(popen_mock.mock_calls, [])
                self.assertListEqual(process_mock.mock_calls, [])

                if 'CONFIG_STACKTRACE=y\n' not in case['kernel_config_contents']:
                    self.assertEqual(
                        processinfo.ProcessInfo.get_kernel_trace(case['process_id']),
                        None
                    )

                    self.assertListEqual(
                        os_path_exists_function_mock.mock_calls,
                        expected_os_path_exists_function_mock_calls
                    )
                    self.assertListEqual(popen_mock.mock_calls, expected_popen_mock_calls)
                    self.assertListEqual(stdout_mock.mock_calls, [])
                    self.assertListEqual(stderr_mock.mock_calls, [])
                    self.assertListEqual(process_mock.mock_calls, expected_process_mock_calls)

                    continue

                expected_open_function_mock_calls = [
                    call('/proc/{}/stack'.format(case['process_id']), 'r'),
                    call().__enter__(),
                    call().read(),
                    call().__exit__(None, None, None)
                ]

                with patch('builtins.open', mock_open(read_data=case['kernel_trace'])) as open_function_mock:
                    self.assertListEqual(open_function_mock.mock_calls, [])

                    actual_kernel_trace = processinfo.ProcessInfo.get_kernel_trace(case['process_id'])

                self.assertEqual(actual_kernel_trace, case['kernel_trace'])

                self.assertListEqual(
                    os_path_exists_function_mock.mock_calls,
                    expected_os_path_exists_function_mock_calls
                )
                self.assertListEqual(popen_mock.mock_calls, expected_popen_mock_calls)
                self.assertListEqual(stdout_mock.mock_calls, [])
                self.assertListEqual(stderr_mock.mock_calls, [])
                self.assertListEqual(process_mock.mock_calls, expected_process_mock_calls)
                self.assertListEqual(open_function_mock.mock_calls, expected_open_function_mock_calls)

    @patch('subprocess.Popen', spec=subprocess.Popen)
    @patch('processinfo.ProcessInfo.get_stack_trace', spec=processinfo.ProcessInfo.get_stack_trace)
    @patch('processinfo.ProcessInfo.get_kernel_trace', spec=processinfo.ProcessInfo.get_kernel_trace)
    @patch('processinfo.ProcessInfo.get_status', spec=processinfo.ProcessInfo.get_status)
    def test_get_process_info(
        self,
        get_status_function_mock: Mock,
        get_kernel_trace_function_mock: Mock,
        get_stack_trace_function_mock: Mock,
        process_mock: Mock
    ) -> None:
        process_status_str = 'dummy process status string'
        kernel_trace_str = 'dummy kernel trace string'
        stack_trace_str = 'dummy stack trace string'
        pid = 1
        expected_mock_function_calls = [call(pid)]

        def reset_mocks() -> None:
            get_status_function_mock.reset_mock()
            get_kernel_trace_function_mock.reset_mock()
            get_stack_trace_function_mock.reset_mock()
            process_mock.reset_mock()

        cases: list[dict[str, Any]] = [
            {
                'setup': (
                    'get_status_function_mock.return_value = "{process_status_str}"\n'
                    'get_kernel_trace_function_mock.return_value = "{kernel_trace_str}"\n'
                    'get_stack_trace_function_mock.return_value = "{stack_trace_str}"\n'
                    'process_mock.pid = {pid}\n'
                    'reset_mocks()\n'
                ).format(
                    process_status_str=process_status_str,
                    kernel_trace_str=kernel_trace_str,
                    stack_trace_str=stack_trace_str,
                    pid=pid
                ),
                'expected_value': (
                    '--- Process status:\n'
                    '{process_status_str}\n'
                    '--- Stack trace:\n'
                    '{stack_trace_str}\n'
                    '--- Kernel trace:\n'
                    '{kernel_trace_str}'
                ).format(
                    process_status_str=process_status_str,
                    stack_trace_str=stack_trace_str,
                    kernel_trace_str=kernel_trace_str
                ),
            },
            {
                'setup': (
                    r'get_status_function_mock.return_value = "{process_status_str}\n"'
                    '\n'
                    r'get_kernel_trace_function_mock.return_value = "{kernel_trace_str}\n"'
                    '\n'
                    r'get_stack_trace_function_mock.return_value = "{stack_trace_str}\n"'
                    '\n'
                    'process_mock.pid = {pid}\n'
                    'reset_mocks()\n'
                ).format(
                    process_status_str=process_status_str,
                    kernel_trace_str=kernel_trace_str,
                    stack_trace_str=stack_trace_str,
                    pid=pid
                ),
                'expected_value': (
                    '--- Process status:\n'
                    '{process_status_str}\n'
                    '--- Stack trace:\n'
                    '{stack_trace_str}\n'
                    '--- Kernel trace:\n'
                    '{kernel_trace_str}'
                ).format(
                    process_status_str=process_status_str,
                    stack_trace_str=stack_trace_str,
                    kernel_trace_str=kernel_trace_str
                ),
            },
            {
                'setup': (
                    r'get_status_function_mock.return_value = "{process_status_str}\n"'
                    '\n'
                    'get_kernel_trace_function_mock.return_value = None\n'
                    r'get_stack_trace_function_mock.return_value = "{stack_trace_str}\n"'
                    '\n'
                    'process_mock.pid = {pid}\n'
                    'reset_mocks()\n'
                ).format(
                    process_status_str=process_status_str,
                    stack_trace_str=stack_trace_str,
                    pid=pid
                ),
                'expected_value': (
                    '--- Process status:\n'
                    '{process_status_str}\n'
                    '--- Stack trace:\n'
                    '{stack_trace_str}'
                ).format(
                    process_status_str=process_status_str,
                    stack_trace_str=stack_trace_str
                ),
            },
        ]

        for case in cases:
            with self.subTest():
                exec(case['setup'])

                self.assertListEqual(get_status_function_mock.mock_calls, [])
                self.assertListEqual(get_kernel_trace_function_mock.mock_calls, [])
                self.assertListEqual(get_stack_trace_function_mock.mock_calls, [])
                self.assertListEqual(process_mock.mock_calls, [])

                self.assertEqual(
                    case['expected_value'],
                    processinfo.ProcessInfo.get_process_info(process_mock)
                )

                self.assertListEqual(get_status_function_mock.mock_calls, expected_mock_function_calls)
                self.assertListEqual(get_kernel_trace_function_mock.mock_calls, expected_mock_function_calls)
                self.assertListEqual(get_stack_trace_function_mock.mock_calls, expected_mock_function_calls)
                self.assertListEqual(process_mock.mock_calls, [])
