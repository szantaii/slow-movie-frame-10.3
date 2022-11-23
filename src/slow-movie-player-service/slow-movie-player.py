#!/usr/bin/env python3

from videolibrary import VideoLibrary
from image import Image
from configuration import Configuration

import os
import time
import subprocess
import argparse


class SlowMoviePlayer:
    def __init__(self, config: Configuration) -> None:
        self.__config = config
        self.__video_library = VideoLibrary(self.__config.video_directory)

    def run(self) -> None:
        image_file_name = 'frame.bmp'

        while True:
            start_time = time.monotonic()

            image = Image(self.__video_library.get_next_frame())

            # (image.resize_with_padding(self.__config.screen_width, self.__config.screen_height)
            #       .save_to_bmp(image_file_name))

            (image.resize_keeping_aspect_ratio(self.__config.screen_width, self.__config.screen_height)
                  .convert_to_grayscale()
                  .apply_4bpp_floyd_steinberg_dithering()
                  .add_padding(self.__config.screen_width, self.__config.screen_height)
                  .convert_to_bgr()
                  .save_to_bmp(image_file_name))

            subprocess.run(['/opt/slow-movie-player/update-screen', '-v', str(self.__config.vcom), '-f', image_file_name])

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
        subprocess.run(['/opt/slow-movie-player/update-screen', '-v', str(config.vcom)])

        exit(0)

    working_directory = os.getenv('RUNTIME_DIRECTORY', '/tmp')
    os.chdir(working_directory)

    SlowMoviePlayer(config).run()
