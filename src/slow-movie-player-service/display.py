from __future__ import annotations
from processinfo import ProcessInfo
import subprocess
import signal
from typing import Any, Optional


class Display:
    TIMEOUT = 30.0
    UPDATE_DISPLAY_PATH = '/opt/slow-movie-player/update-display'

    def __init__(self, vcom: float, file_path: str) -> None:
        self.__vcom = vcom
        self.__file_path = file_path
        self.__update_process: Optional[subprocess.Popen] = None
        self.__original_sigterm_handler = signal.getsignal(signal.SIGTERM)

    def __enter__(self) -> Display:
        return self

    def __exit__(self, *_: Any) -> None:
        self.__stop()

    def __start(self) -> None:
        signal.signal(signal.SIGTERM, self.__sigterm_handler)
        signal.signal(signal.SIGUSR1, self.__noop_signal_handler)

        self.__update_process = subprocess.Popen(
            [
                self.__class__.UPDATE_DISPLAY_PATH,
                '-d',
                '-v',
                str(self.__vcom),
                '-f',
                self.__file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        try:
            signal.sigtimedwait([signal.SIGUSR1], self.__class__.TIMEOUT)
        except InterruptedError as error:
            self.__stop()

            raise error

    def __stop(self) -> None:
        if self.__update_process is None:
            return

        self.__update_process.send_signal(signal.SIGTERM)
        self.__handle_process_shutdown(self.__update_process, self.__class__.TIMEOUT)

        self.__update_process = None

    @staticmethod
    def __handle_process_shutdown(process: subprocess.Popen, timeout: float) -> None:
        try:
            output = process.communicate(timeout=timeout)[0]
        except subprocess.TimeoutExpired:
            process_info = ProcessInfo.get_process_info(process)

            process.kill()
            output = process.communicate()[0]

            raise RuntimeError(
                'Timeout during updating display.\n{}Process info:\n{}'.format(
                    "Process output: '{}'.\n".format(output) if output else '',
                    process_info
                )
            )

        if process.returncode != 0:
            raise RuntimeError(
                "Error during updating display ({}){}.".format(
                    process.returncode,
                    ": '{}'".format(output) if output else ''
                )
            )

    def __sigterm_handler(self, *_: Any) -> None:
        self.__stop()
        signal.signal(signal.SIGTERM, self.__original_sigterm_handler)
        signal.raise_signal(signal.SIGTERM)

    @staticmethod
    def __noop_signal_handler(*_: Any) -> None:
        pass

    def update(self) -> None:
        if self.__update_process is None:
            self.__start()

        self.__update_process.send_signal(signal.SIGUSR1)

        try:
            signal.sigtimedwait([signal.SIGUSR1], self.__class__.TIMEOUT)
        except InterruptedError as error:
            self.__stop()

            raise error

    @classmethod
    def clear(cls, vcom: float) -> None:
        update_process = subprocess.Popen(
            [
                cls.UPDATE_DISPLAY_PATH,
                '-v',
                str(vcom)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        cls.__handle_process_shutdown(update_process, cls.TIMEOUT)
