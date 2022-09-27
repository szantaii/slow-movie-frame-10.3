#!/usr/bin/env python3

from videolibrary import VideoLibrary
from image import Image
from configuration import Configuration

import os
import time
import subprocess
import argparse


class SlowMoviePlayer():
    def __init__(self, config: Configuration, runtime_directory: str) -> None:
        self.__config = config
        self.__video_library = VideoLibrary(self.__config.video_directory)
        self.__image_file_path = os.path.join(runtime_directory, 'frame.bmp')

    def run(self) -> None:
        while True:
            start_time = time.monotonic()

            image = Image(self.__video_library.get_next_frame())
            image.resize_with_padding(self.__config.display_horizontal_resolution, self.__config.display_vertical_resolution).save_to_bmp(self.__image_file_path)
            subprocess.run(['/opt/slow-movie-player/update-screen', '-v', self.__config.vcom, '-f', self.__image_file_path])

            elapsed_time = time.monotonic() - start_time

            if elapsed_time < self.__config.refresh_timeout:
                time.sleep(self.__config.refresh_timeout - elapsed_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--clear-screen', action='store_true')
    args = parser.parse_args()

    config_directory = os.getenv('CONFIGURATION_DIRECTORY', '/etc/slow-movie-player')
    config = Configuration(config_directory)

    if args.clear_screen:
        subprocess.run(['/opt/slow-movie-player/update-screen', '-v', config.vcom])

        exit(0)

    runtime_directory = os.getenv('RUNTIME_DIRECTORY', '/tmp')

    SlowMoviePlayer(config, runtime_directory).run()
