#!/usr/bin/env python3

from videolibrary import VideoLibrary
from image import Image
from configuration import Configuration
from display import Display

import os
import time
import argparse


class SlowMoviePlayer:
    def __init__(self, config: Configuration) -> None:
        self.__config = config
        self.__video_library = VideoLibrary(self.__config.video_directory)

    def run(self) -> None:
        # image_file_name = 'frame.bmp'
        image_file_name = 'frame.4bpp'

        with Display(self.__config.vcom, image_file_name) as display:
            while True:
                start_time = time.monotonic()

                if self.__config.random_frame:
                    image = Image(self.__video_library.get_random_frame())
                else:
                    image = Image(self.__video_library.get_next_frame(self.__config.skip))

                # (image.resize_with_padding(self.__config.screen_width, self.__config.screen_height)
                #       .save_to_bmp(image_file_name))

                # (image.resize_keeping_aspect_ratio(self.__config.screen_width, self.__config.screen_height)
                #       .apply_4bpp_floyd_steinberg_dithering()
                #       .add_padding(self.__config.screen_width, self.__config.screen_height)
                #       .convert_to_bgr()
                #       .save_to_bmp(image_file_name))

                (image.resize_keeping_aspect_ratio(self.__config.screen_width, self.__config.screen_height)
                      .apply_4bpp_floyd_steinberg_dithering(self.__config.grayscale_method)
                      .add_padding(self.__config.screen_width, self.__config.screen_height)
                      .save_to_custom_4bpp_image(image_file_name))

                display.update()

                elapsed_time = time.monotonic() - start_time

                if elapsed_time < self.__config.refresh_timeout:
                    time.sleep(self.__config.refresh_timeout - elapsed_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--clear', action='store_true')
    args = parser.parse_args()

    config_directory = os.getenv('CONFIGURATION_DIRECTORY', '/etc/slow-movie-player')
    config = Configuration(config_directory)

    if args.clear:
        Display.clear(config.vcom)

        exit(0)

    working_directory = os.getenv('RUNTIME_DIRECTORY', '/tmp')
    os.chdir(working_directory)

    SlowMoviePlayer(config).run()
