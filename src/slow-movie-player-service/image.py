from __future__ import annotations
import cv2
import numpy
import subprocess
import os


class Image():
    BMP_FILE_EXTENSION = '.bmp'
    SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE = (
        'gray_palette.pgm',
        (
            'P2\n'
            '1 16\n'
            '255\n'
            '0 17 34 51 68 85 102 119 136 153 170 187 204 221 238 255\n'
        )
    )

    def __init__(self, image: numpy.ndarray) -> None:
        self.__image = image

        if not os.path.exists(self.__class__.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[0]):
            with open(self.__class__.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[0], 'w') as palette_file:
                palette_file.write(self.__class__.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[1])

    def resize_keeping_aspect_ratio(self, max_width: int, max_height: int) -> Image:
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

    def add_padding(self, padded_width: int, padded_height: int) -> Image:
        height, width = self.__image.shape[:2]
        x_offset = (padded_width - width) // 2
        y_offset = (padded_height - height) // 2
        shape = (padded_height, padded_width) if len(self.__image.shape) < 3 else (padded_height, padded_width, 3)

        padded_image = numpy.zeros(shape, dtype=numpy.uint8)
        padded_image[y_offset:y_offset + height, x_offset:x_offset + width] = self.__image
        self.__image = padded_image

        return self

    def resize_with_padding(self, width: int, height: int) -> Image:
        return (self.resize_keeping_aspect_ratio(width, height)
                    .add_padding(width, height))

    def convert_to_bgr(self) -> Image:
        self.__image = cv2.cvtColor(self.__image, cv2.COLOR_GRAY2BGR)

        return self

    def apply_4bpp_floyd_steinberg_dithering(self) -> Image:
        imagemagick_command = [
            'convert',
            '-',
            '-grayscale',
            'Rec601Luminance',
            '-dither',
            'FloydSteinberg',
            '-remap',
            self.__class__.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[0],
            'pgm:-'
        ]

        is_encoded, ppm_image = cv2.imencode('.ppm', self.__image)

        if not is_encoded:
            raise RuntimeError('Image conversion failed! Cannot encode image into PPM format.')

        convert_process = subprocess.Popen(
            imagemagick_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        pgm_image, stderr = convert_process.communicate(input=ppm_image.tobytes())

        if convert_process.returncode != 0:
            raise RuntimeError("Failed to apply Floyd-Steinberg dithering: '{}'.".format(stderr))

        pgm_image_data = numpy.asarray(bytearray(pgm_image), dtype=numpy.uint8)

        self.__image = cv2.imdecode(pgm_image_data, cv2.IMREAD_GRAYSCALE)

        return self

    def save_to_bmp(self, file_path: str) -> None:
        if not file_path.lower().endswith(self.__class__.BMP_FILE_EXTENSION):
            raise ValueError(
                "File name in argument 'file_path' must end in '{}' extension.".format(
                    self.__class__.BMP_FILE_EXTENSION
                )
            )

        cv2.imwrite(file_path, self.__image)

    def save_to_custom_4bpp_image(self, file_path: str) -> None:
        """
        Save image into a four bits per pixel format

        The image format is the following:

            +-------------------------------------------------------------+
            | 2 bytes encoding the image width in pixels (little endian)  |
            +-------------------------------------------------------------+
            | 2 bytes encoding the image height in pixels (little endian) |
            +-------------------------------------------------------------+
            | image data: Each following byte encodes two pixels of the   |
            |             image. The upper four bits encode the first     |
            |             pixel, the lower four bits the next pixel and   |
            |             so on. Pixels are encoded from top to bottom    |
            |             row by row, from right to left.                 |
            +-------------------------------------------------------------+

            0        1        2        3        4        (width * height) / 2 + 3
            +--------+--------+--------+--------+- . . . +--------+
            |        |        |        |        |        |        |
            +--------+--------+--------+--------+- . . . +--------+
            :                 :                 :
            :   image width   :  image height   :
            :     2 bytes     :     2 bytes     :
            :  little endian  :  little endian  :
            :                 :                 :

        Notes:
            * It is not required to have any image data at all.
            * The minimum file size is 4 bytes.
            * The maximum image resolution is 2^16 - 2 pixels by 2^16 - 1 pixels
              or vice versa (resulting in a 2,147,385,349 bytes of maximum file size).
            * The number of pixels in the image must be even: (width * height) mod 2 == 0.
            * The last index of the last byte (the last two pixels if image has data)
              is (width * height) / 2 + 3.
        """

        if len(self.__image.shape) != 2:
            raise RuntimeError(
                'Saving images to the custom 4 bits per pixel format can only work with images with a single color channel. '
                'You must reduce the number of color channels to one to use this function!'
            )

        height, width = self.__image.shape[:2]
        max_resolution = 2**16 - 1

        if not (width <= max_resolution and height < max_resolution
                or width < max_resolution and height <= max_resolution):
            raise RuntimeError(
                'Image resolution is too high! '
                'Maximum image resolution is {}x{} (or vice versa).'.format(max_resolution, max_resolution - 1)
            )

        pixel_count = width * height

        if pixel_count % 2 != 0:
            raise RuntimeError(
                'The number of pixels in image is odd! '
                'Images with odd number of pixels cannot be saved.'
            )

        image_file_header = bytearray()
        image_file_header.extend(width.to_bytes(length=2, byteorder='little'))
        image_file_header.extend(height.to_bytes(length=2, byteorder='little'))

        image_file_data = bytearray()
        top_four_bits_mask = numpy.uint8(0b11110000)
        bottom_four_bits_mask = numpy.uint8(0b00001111)
        flat_image = numpy.reshape(
            numpy.fliplr(self.__image),
            pixel_count,
            order='C'
        )

        for i in range(0, pixel_count, 2):
            image_file_data.append(
                (flat_image[i] & top_four_bits_mask) | (flat_image[i + 1] & bottom_four_bits_mask)
            )

        with open(file_path, 'wb') as image_file:
            image_file.write(image_file_header)
            image_file.write(image_file_data)
