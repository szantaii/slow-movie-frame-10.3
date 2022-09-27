import cv2
import numpy


class Video:
    def __init__(self, file_path: str) -> None:
        self.__video = cv2.VideoCapture(file_path)

    def __del__(self) -> None:
        self.__video.release()

    def get_frame_count(self) -> int:
        return int(self.__video.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_frame(self, frame_index: int) -> numpy.ndarray:
        self.__video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        is_read, frame = self.__video.read()

        if not is_read:
            frame = numpy.empty((0, 0), dtype=numpy.uint8)

        return frame
