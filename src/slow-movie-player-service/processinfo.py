import os
import subprocess
from typing import Optional


class ProcessInfo:
    @staticmethod
    def get_status(pid: int) -> str:
        with open('/proc/{}/status'.format(pid), 'r') as status_file:
            return status_file.read()

    @staticmethod
    def get_kernel_trace(pid: int) -> Optional[str]:
        kernel_config_file_path = '/proc/config.gz'

        if not os.path.exists(kernel_config_file_path):
            return None

        kernel_config_process = subprocess.Popen(
            ['zcat', kernel_config_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        kernel_configs = kernel_config_process.communicate()[0]

        if 'CONFIG_STACKTRACE=y\n' not in kernel_configs:
            return None

        with open('/proc/{}/stack'.format(pid), 'r') as kernel_stack_file:
            return kernel_stack_file.read()

    @staticmethod
    def get_stack_trace(pid: int) -> str:
        stack_trace_command = [
            'gdb',
            '-ex', 'set pagination off',
            '-ex', 'attach {}'.format(pid),
            '-ex', 'thread apply all bt full',
            '-ex', 'detach',
            '-ex', 'q'
        ]

        stack_trace_process = subprocess.Popen(
            stack_trace_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        return stack_trace_process.communicate()[0]

    @classmethod
    def get_process_info(cls, process: subprocess.Popen) -> str:
        status = cls.get_status(process.pid)
        kernel_trace = cls.get_kernel_trace(process.pid)
        stack_trace = cls.get_stack_trace(process.pid)

        process_info = '--- Process status:\n{}'.format(status)

        if not process_info.endswith('\n'):
            process_info += '\n'

        process_info += '--- Stack trace:\n{}'.format(stack_trace)

        if kernel_trace:
            if not process_info.endswith('\n'):
                process_info += '\n'

            process_info += '--- Kernel trace:\n{}'.format(kernel_trace)

        return process_info.rstrip('\n')
