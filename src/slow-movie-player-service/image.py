from __future__ import annotations
import cv2
import numpy
import inspect


class Image():
    BMP_FILE_EXTENSION = '.bmp'

    def __init__(self, image: numpy.ndarray) -> None:
        self.__image = image

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

    def convert_to_grayscale(self) -> Image:
        self.__image = cv2.cvtColor(self.__image, cv2.COLOR_BGR2GRAY)

        return self

    def convert_to_bgr(self) -> Image:
        self.__image = cv2.cvtColor(self.__image, cv2.COLOR_GRAY2BGR)

        return self

    def __assert_image_has_only_one_color_channel(self) -> None:
        if len(self.__image.shape) != 2:
            caller_function_name = 'the caller method'
            current_frame = inspect.currentframe()

            if current_frame is not None and current_frame.f_back is not None:
                caller_function_name = "method '{}'".format(current_frame.f_back.f_code.co_name)

            raise RuntimeError(
                '{} can only work with images with a single color channel.\n'
                'You must reduce the number of color channels to one to use {}!'.format(
                    caller_function_name.capitalize(),
                    caller_function_name
                )
            )

    def apply_4bpp_floyd_steinberg_dithering(self) -> Image:
        self.__assert_image_has_only_one_color_channel()

        grays = numpy.array([i * 17 for i in range(16)])
        border = 1
        temp_image = cv2.copyMakeBorder(self.__image, border, border, border, border, cv2.BORDER_REPLICATE)
        height, width = temp_image.shape

        def get_nearest_color(color):
            return grays[numpy.absolute(grays - color).argmin()]

        for i in range(1, height - 1):
            for j in range(1, width - 1):
                old_value = temp_image[i][j]
                new_value = get_nearest_color(old_value)
                temp_image[i][j] = new_value

                quant_err = old_value - new_value

                temp_image[i][j + 1] += quant_err * 7 / 16
                temp_image[i + 1][j - 1] += quant_err * 3 / 16
                temp_image[i + 1][j] += quant_err * 5 / 16
                temp_image[i + 1][j + 1] += quant_err / 16

        self.__image = temp_image[1:height - 1, 1:width - 1]

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
        self.__assert_image_has_only_one_color_channel()

        height, width = self.__image.shape[:2]

        max_resolution = 2**16 - 1

        if width > max_resolution or height > max_resolution:
            raise RuntimeError(
                'Image resolution is too high! '
                'Maximum image resolution is {0}x{0}.'.format(max_resolution)
            )

        pixel_count = width * height

        if pixel_count % 2 != 0:
            raise RuntimeError(
                'The number of pixels in image is odd! '
                'Images with odd number of pixels cannot be saved.'
            )

        image_file_header = bytearray()
        image_file_header.extend((width).to_bytes(length=2, byteorder='little'))
        image_file_header.extend((height).to_bytes(length=2, byteorder='little'))

        image_file_data = bytearray()
        top_four_bits_mask = numpy.uint8(0b11110000)
        bottom_four_bits_mask = numpy.uint8(0b00001111)
        flat_image = numpy.reshape(self.__image, pixel_count, order='F')

        for i in range(0, pixel_count, 2):
            image_file_data.append(
                ((flat_image[i] & top_four_bits_mask) | (flat_image[i + 1] & bottom_four_bits_mask)).tobytes()
            )

        with open(file_path, 'wb') as image_file:
            image_file.write(image_file_header)
            image_file.write(image_file_data)
