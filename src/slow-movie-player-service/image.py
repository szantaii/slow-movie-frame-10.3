from __future__ import annotations

import cv2
import numpy


class Image():
    BMP_FILE_EXTENSION = '.bmp'

    def __init__(self, image: numpy.ndarray) -> None:
        self.__image = image

    def __resize_keeping_aspect_ratio(self, max_width: int, max_height: int) -> Image:
        height, width = self.__image.shape[:2]
        new_width = None
        new_height = None

        if width / height <= max_width / max_height:
            new_width = int(width * (max_height / height))
            new_height = max_height
        else:
            new_width = max_width
            new_height = int(height * (max_width / width))

        # From OpenCV documentation:
        #
        # To shrink an image, it will generally look best with INTER_AREA
        # interpolation, whereas to enlarge an image, it will generally look
        # best with INTER_CUBIC (slow) or INTER_LINEAR
        # (faster but still looks OK).
        interpolation = cv2.INTER_AREA

        if new_width > width or new_height > height:
            interpolation = cv2.INTER_CUBIC

        self.__image = cv2.resize(self.__image, (new_width, new_height), interpolation=interpolation)

        return self

    def __add_padding(self, padded_width: int, padded_height: int) -> Image:
        height, width = self.__image.shape[:2]
        x_offset = (padded_width - width) // 2
        y_offset = (padded_height - height) // 2

        padded_image = numpy.zeros((padded_height, padded_width, 3), dtype=numpy.uint8)
        padded_image[y_offset:y_offset + height, x_offset:x_offset + width] = self.__image
        self.__image = padded_image

        return self

    def resize_with_padding(self, width: int, height: int) -> Image:
        return (self.__resize_keeping_aspect_ratio(width, height)
                    .__add_padding(width, height))

    def save_to_bmp(self, file_path: str) -> None:
        if not file_path.lower().endswith(self.__class__.BMP_FILE_EXTENSION):
            raise ValueError("file_path must have '{}' extension.".format(self.__class__.BMP_FILE_EXTENSION))

        cv2.imwrite(file_path, self.__image)
