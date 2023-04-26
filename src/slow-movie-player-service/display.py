from processinfo import ProcessInfo
import subprocess
from typing import Optional


class Display:
    @staticmethod
    def __update(
        vcom: float,
        file_path: str = '',
        timeout: Optional[int] = None
    ) -> None:
        command = ['/opt/slow-movie-player/update-display', '-v', str(vcom)]

        if file_path:
            command += ['-f', file_path]

        update_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        try:
            output = update_process.communicate(timeout=timeout)[0]
        except subprocess.TimeoutExpired:
            status = ProcessInfo.get_status(update_process.pid)
            kernel_trace = ProcessInfo.get_kernel_trace(update_process.pid)
            stack_trace = ProcessInfo.get_stack_trace(update_process.pid)

            error_message = (
                'Timeout during updating display.\n'
                '--- Process status:\n{}'
            ).format(status)

            if not error_message.endswith('\n'):
                error_message += '\n'

            error_message += '--- Stack trace:\n{}'.format(stack_trace)

            if kernel_trace:
                if not error_message.endswith('\n'):
                    error_message += '\n'

                error_message += '--- Kernel trace:\n{}'.format(kernel_trace)

            update_process.kill()
            output = update_process.communicate()[0]

            if output:
                if not error_message.endswith('\n'):
                    error_message += '\n'

                error_message += '--- Output:\n{}'.format(output)

            raise RuntimeError(error_message)

        if update_process.returncode != 0:
            raise RuntimeError(
                "Error during updating display ({}){}.".format(
                    update_process.returncode,
                    ": '{}'".format(output) if output else ''
                )
            )

    @classmethod
    def clear(cls, vcom: float) -> None:
        cls.__update(vcom)

    @classmethod
    def draw_image(cls, vcom: float, file_path: str) -> None:
        cls.__update(vcom, file_path=file_path, timeout=60)
