from video import Video
from skip import FrameSkip, TimeSkip

from typing import Union
from collections import OrderedDict
import json
import numpy
import os


class VideoLibrary:
    PLAYBACK_INFO_FILE_NAME = 'videos.json'
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
        self.__playback_info = OrderedDict()
        self.__video_directory = video_directory

        self.__playback_info_file_path = os.path.join(self.__video_directory, self.__class__.PLAYBACK_INFO_FILE_NAME)

        self.__temp_playback_info_file_path = '{}{}'.format(
            self.__playback_info_file_path,
            self.__class__.TEMPORARY_FILE_EXTENSION
        )

        self.__backup_playback_info_file_path = '{}{}'.format(
            self.__playback_info_file_path,
            self.__class__.BACKUP_FILE_EXTENSION
        )

        self.__load_from_file()
        self.__discover()
        self.__save_to_file()

    def __load_from_file(self) -> None:
        try:
            with open(self.__playback_info_file_path) as playback_info_file:
                playback_info_file_contents = playback_info_file.read()

                try:
                    self.__playback_info = json.loads(playback_info_file_contents, object_pairs_hook=OrderedDict)
                except json.JSONDecodeError as error:
                    print(
                        "Caught exception: '{}'!\n"
                        "Cannot load playback information from '{}'.".format(error.msg, self.__playback_info_file_path)
                    )
        except FileNotFoundError:
            print(
                "File '{}' does not exist! "
                'Cannot load playback information.'.format(self.__playback_info_file_path)
            )

    def __compare_playback_info_to_file(self, file_path: str) -> None:
        playback_info_string = json.dumps(self.__playback_info, ensure_ascii=False, indent=4)

        with open(file_path, 'r') as playback_info_file:
            playback_info_file_contents = playback_info_file.read()

        if playback_info_string != playback_info_file_contents:
            raise ValueError('we are fucked')

    def __save_to_file(self) -> None:
        temp_playback_info_file = os.open(
            self.__temp_playback_info_file_path,
            os.O_CREAT | os.O_WRONLY
        )

        os.write(
            temp_playback_info_file,
            json.dumps(self.__playback_info, ensure_ascii=False, indent=4).encode('utf-8')
        )
        os.fsync(temp_playback_info_file)
        os.close(temp_playback_info_file)

        self.__compare_playback_info_to_file(self.__temp_playback_info_file_path)

        if os.access(self.__playback_info_file_path, os.F_OK, follow_symlinks=False):
            os.rename(self.__playback_info_file_path, self.__backup_playback_info_file_path)

        os.rename(self.__temp_playback_info_file_path, self.__playback_info_file_path)

        self.__compare_playback_info_to_file(self.__playback_info_file_path)

        if os.access(self.__backup_playback_info_file_path, os.F_OK, follow_symlinks=False):
            os.unlink(self.__backup_playback_info_file_path)

    def __reset(self) -> None:
        for _, info in self.__playback_info.items():
            info['next_frame'] = 0
            info['next_timestamp'] = 0.0

        self.__save_to_file()

    def __discover(self) -> None:
        video_paths = list(self.__playback_info.keys())

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
            if video_path not in self.__playback_info.keys():
                video = Video(video_path)
                frame_count, duration = video.get_stats()
                self.__playback_info[video_path] = OrderedDict(
                    {
                        'frame_count': frame_count,
                        'duration': duration,
                        'next_frame': 0,
                        'next_timestamp': 0.0
                    }
                )

                continue

            if not os.path.exists(video_path):
                del self.__playback_info[video_path]

                continue

            video = Video(video_path)
            frame_count, duration = video.get_stats()

            if (self.__playback_info[video_path]['frame_count'] != frame_count
                    or self.__playback_info[video_path]['duration'] != duration):
                self.__playback_info[video_path]['frame_count'] = frame_count
                self.__playback_info[video_path]['duration'] = duration
                self.__playback_info[video_path]['next_frame'] = 0
                self.__playback_info[video_path]['next_timestamp'] = 0.0

    def get_next_frame(self, skip: Union[FrameSkip, TimeSkip] = FrameSkip(1)) -> numpy.ndarray:
        if not isinstance(skip, (FrameSkip, TimeSkip)):
            raise TypeError(
                "Argument 'skip' is of type '{}', but should be of type '{}' or '{}' instead.".format(
                    type(skip),
                    FrameSkip,
                    TimeSkip
                )
            )

        last_video_path = next(reversed(self.__playback_info))

        for video_path, info in self.__playback_info.items():
            if (info['next_frame'] < info['frame_count']
                    and info['next_timestamp'] < info['duration']):
                video = Video(video_path)
                frame_rate = video.get_frame_rate()

                if isinstance(skip, FrameSkip):
                    frame = video.get_frame(info['next_frame'])
                    info['next_frame'] += skip.amount
                    info['next_timestamp'] = (info['next_frame'] / frame_rate) * 1000.0
                else:
                    frame = video.get_frame(info['next_timestamp'])
                    info['next_timestamp'] += skip.amount
                    info['next_frame'] = int((info['next_timestamp'] / 1000.0) * frame_rate)

                self.__save_to_file()

                return frame

            if video_path == last_video_path:
                self.__reset()

                return self.get_next_frame(skip=skip)
