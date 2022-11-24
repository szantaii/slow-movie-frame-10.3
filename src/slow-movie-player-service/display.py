import subprocess


class Display:
    @staticmethod
    def __update(vcom: float, file_path: str = '') -> None:
        command = ['/opt/slow-movie-player/update-screen', '-v', str(vcom)]

        if file_path:
            command += ['-f', file_path]

        update_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = update_process.communicate()

        if update_process.returncode != 0:
            raise RuntimeError("Error during updating display: '{}'.".format(output))

    @classmethod
    def clear(cls, vcom: float) -> None:
        cls.__update(vcom)

    @classmethod
    def draw_image(cls, vcom: float, file_path: str) -> None:
        cls.__update(vcom, file_path=file_path)
