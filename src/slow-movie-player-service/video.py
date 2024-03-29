import cv2
import numpy
from typing import Union


class Video:
    def __init__(self, file_path: str) -> None:
        self.__video = cv2.VideoCapture(file_path)

    def __del__(self) -> None:
        self.__video.release()

    def get_frame_rate(self) -> float:
        return self.__video.get(cv2.CAP_PROP_FPS)

    def get_stats(self) -> tuple[int, float]:
        frame_rate = self.get_frame_rate()
        frame_count = int(self.__video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = (frame_count / frame_rate) * 1000.0

        return frame_count, duration

    def get_frame(self, position: Union[int, float]) -> numpy.ndarray:
        if not isinstance(position, (int, float)):
            raise TypeError(
                "Argument 'position' must be of type '{}' or '{}', but '{}' was provided instead.".format(
                    int,
                    float,
                    type(position)
                )
            )

        if position < 0:
            raise ValueError(
                "Value of argument 'position' must be a non-negative number, but {} was provided instead.".format(
                    position
                )
            )

        if isinstance(position, int):
            self.__video.set(cv2.CAP_PROP_POS_FRAMES, position)
        else:
            self.__video.set(cv2.CAP_PROP_POS_MSEC, position)

        is_read, frame = self.__video.read()

        if not is_read:
            raise RuntimeError('Unable to read video frame.')

        return frame
