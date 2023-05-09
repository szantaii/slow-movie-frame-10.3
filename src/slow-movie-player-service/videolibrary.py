from video import Video
from skip import FrameSkip, TimeSkip

from typing import Union
from collections import OrderedDict
import json
import numpy
import os
import random


class VideoLibrary:
    VIDEO_LIBRARY_FILE_NAME = 'videos.json'
    BACKUP_FILE_EXTENSION = '.bak'
    TEMPORARY_FILE_EXTENSION = '.tmp'
    VIDEO_FILE_EXTENSIONS = (
        '.avi',
        '.mkv',
        '.mov',
        '.mp4',
        '.webm',
    )

    def __init__(self, video_directory: str) -> None:
        if not os.path.exists(video_directory):
            raise FileNotFoundError("Video directory '{}' does not exist.".format(video_directory))

        self.__video_library: OrderedDict = OrderedDict()
        self.__video_directory: str = video_directory

        self.__video_library_file_path: str = os.path.join(
            self.__video_directory,
            self.__class__.VIDEO_LIBRARY_FILE_NAME
        )

        self.__temp_video_library_file_path: str = '{}{}'.format(
            self.__video_library_file_path,
            self.__class__.TEMPORARY_FILE_EXTENSION
        )

        self.__backup_video_library_file_path: str = '{}{}'.format(
            self.__video_library_file_path,
            self.__class__.BACKUP_FILE_EXTENSION
        )

        self.__load_from_file()
        self.__discover()
        self.__save_to_file()

    def __load_from_file(self) -> None:
        if not os.path.exists(self.__video_library_file_path):
            return

        with open(self.__video_library_file_path) as video_library_file:
            video_library_file_contents = video_library_file.read()

        try:
            self.__video_library = json.loads(video_library_file_contents, object_pairs_hook=OrderedDict)
        except json.JSONDecodeError as error:
            raise ValueError(
                (
                    "Cannot load video library from '{}'. "
                    "It is recommended to check for backup ('{}') and temporary ('{}') files in '{}' "
                    'for manually recovering video library data. '
                    "See details for easier debugging: '{}'."
                ).format(
                    self.__video_library_file_path,
                    self.__class__.BACKUP_FILE_EXTENSION,
                    self.__class__.TEMPORARY_FILE_EXTENSION,
                    self.__video_directory,
                    error.__repr__()
                )
            )

    def __compare_video_library_to_file(self, file_path: str) -> None:
        video_library_string = json.dumps(self.__video_library, ensure_ascii=False, indent=4)

        with open(file_path, 'r') as video_library_file:
            video_library_file_contents = video_library_file.read()

        if video_library_string != video_library_file_contents:
            raise ValueError(
                (
                    "Cannot save video library to '{}'. "
                    "It is recommended to check for backup ('{}') and temporary ('{}') files in '{}' "
                    'for manually recovering video library data.'
                ).format(
                    self.__video_library_file_path,
                    self.__class__.BACKUP_FILE_EXTENSION,
                    self.__class__.TEMPORARY_FILE_EXTENSION,
                    self.__video_directory
                )
            )

    def __save_to_file(self) -> None:
        temp_video_library_file = os.open(
            self.__temp_video_library_file_path,
            os.O_CREAT | os.O_WRONLY
        )

        os.write(
            temp_video_library_file,
            json.dumps(self.__video_library, ensure_ascii=False, indent=4).encode('utf-8')
        )
        os.fsync(temp_video_library_file)
        os.close(temp_video_library_file)

        self.__compare_video_library_to_file(self.__temp_video_library_file_path)

        if os.access(self.__video_library_file_path, os.F_OK, follow_symlinks=False):
            os.rename(self.__video_library_file_path, self.__backup_video_library_file_path)

        os.rename(self.__temp_video_library_file_path, self.__video_library_file_path)

        self.__compare_video_library_to_file(self.__video_library_file_path)

        if os.access(self.__backup_video_library_file_path, os.F_OK, follow_symlinks=False):
            os.unlink(self.__backup_video_library_file_path)

    def __reset(self) -> None:
        for _, video_info in self.__video_library.items():
            video_info['next_frame'] = 0
            video_info['next_timestamp'] = 0.0

        self.__save_to_file()

    def __discover(self) -> None:
        video_paths = list(self.__video_library.keys())

        for root_directory, _, files in os.walk(self.__video_directory):
            for file in files:
                file_path = os.path.join(root_directory, file)

                if (file_path.lower().endswith(self.__class__.VIDEO_FILE_EXTENSIONS)
                        and file_path not in video_paths):
                    video_paths.append(file_path)

        if not video_paths:
            return

        video_paths = sorted(video_paths)

        for video_path in video_paths:
            if video_path not in self.__video_library.keys():
                video = Video(video_path)
                frame_count, duration = video.get_stats()
                self.__video_library[video_path] = OrderedDict(
                    {
                        'frame_count': frame_count,
                        'duration': duration,
                        'next_frame': 0,
                        'next_timestamp': 0.0
                    }
                )

                continue

            if not os.path.exists(video_path):
                del self.__video_library[video_path]

                continue

            video = Video(video_path)
            frame_count, duration = video.get_stats()

            if (self.__video_library[video_path]['frame_count'] != frame_count
                    or self.__video_library[video_path]['duration'] != duration):
                self.__video_library[video_path]['frame_count'] = frame_count
                self.__video_library[video_path]['duration'] = duration
                self.__video_library[video_path]['next_frame'] = 0
                self.__video_library[video_path]['next_timestamp'] = 0.0

    def __raise_on_empty_video_library(self) -> None:
        if not self.__video_library:
            raise RuntimeError('Cannot get frame from empty video library!')

    def get_next_frame(self, skip: Union[FrameSkip, TimeSkip] = FrameSkip(1)) -> numpy.ndarray:
        self.__raise_on_empty_video_library()

        if not isinstance(skip, (FrameSkip, TimeSkip)):
            raise TypeError(
                "Argument 'skip' is of type '{}', but should be of type '{}' or '{}' instead.".format(
                    type(skip),
                    FrameSkip,
                    TimeSkip
                )
            )

        last_video_path = next(reversed(self.__video_library))

        for video_path, video_info in self.__video_library.items():
            if (video_info['next_frame'] < video_info['frame_count']
                    and video_info['next_timestamp'] < video_info['duration']):
                video = Video(video_path)
                frame_rate = video.get_frame_rate()

                if isinstance(skip, FrameSkip):
                    frame = video.get_frame(video_info['next_frame'])
                    video_info['next_frame'] += skip.amount
                    video_info['next_timestamp'] = (video_info['next_frame'] / frame_rate) * 1000.0
                else:
                    frame = video.get_frame(video_info['next_timestamp'])
                    video_info['next_timestamp'] += skip.amount
                    video_info['next_frame'] = int((video_info['next_timestamp'] / 1000.0) * frame_rate)

                self.__save_to_file()

                return frame

            if video_path == last_video_path:
                self.__reset()

                return self.get_next_frame(skip=skip)

    def get_random_frame(self) -> numpy.ndarray:
        self.__raise_on_empty_video_library()

        video_path, video_info = random.choice(list(self.__video_library.items()))
        frame_index = random.randint(0, video_info['frame_count'] - 1)
        video = Video(video_path)

        return video.get_frame(frame_index)
