from module_helper import get_module_from_file
from unittest import TestCase
import numpy
import tempfile
import os
from typing import List, Tuple, Union

image = get_module_from_file('../../src/slow-movie-player-service/image.py')


class ImageTest(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.original_working_directory = os.getcwd()
        self.test_directory_path = tempfile.mkdtemp()
        self.bmp_image_file_path = os.path.join(self.test_directory_path, 'image.bmp')
        self.four_bits_per_pixel_image_file_path = os.path.join(self.test_directory_path, 'image.4bpp')

        os.chdir(self.test_directory_path)

    def tearDown(self) -> None:
        os.chdir(self.original_working_directory)

        image_16_color_palette_file_path = os.path.join(
            self.test_directory_path,
            image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[0]
        )

        test_file_paths = [
            image_16_color_palette_file_path,
            self.bmp_image_file_path,
            self.four_bits_per_pixel_image_file_path
        ]

        for test_file_path in test_file_paths:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)

        os.rmdir(self.test_directory_path)

        super().tearDown()

    @staticmethod
    def get_image_data(img) -> Union[List[List[int]], List[List[List[int]]]]:
        return img._Image__image.tolist()

    @staticmethod
    def get_image_shape(img) -> Tuple:
        return img._Image__image.shape

    def test_instantiation_with_wrong_input_array_data_types(self) -> None:
        wrong_data_types = [
            numpy.uint,
            numpy.uint16,
            numpy.uintp,
            numpy.int8,
            numpy.int16,
            'i4',  # numpy.int32
            numpy.float16,
            numpy.float32,
            numpy.float64,
            str,
        ]

        for wrong_data_type in wrong_data_types:
            with self.subTest(wrong_data_type=wrong_data_type):
                self.assertRaisesRegex(
                    ValueError,
                    r"Value of attribute 'dtype' of 'image' is not '<class 'numpy\.uint8'>'\.$",
                    image.Image,
                    numpy.ndarray((1, 1, 3), dtype=wrong_data_type)
                )

                self.assertFalse(os.path.exists(self.four_bits_per_pixel_image_file_path))

    def test_palette_file_exists_after_instantiation(self) -> None:
        image.Image(numpy.ndarray((0, 0, 3), dtype=numpy.uint8))

        self.assertTrue(os.path.exists(image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[0]))
        self.assertTrue(os.path.isfile(image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[0]))

        with open(image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[0]) as palette_file:
            palette_file_contents = palette_file.read()

        self.assertEqual(
            palette_file_contents,
            image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[1]
        )

    def test_resize_keeping_aspect_ratio(self) -> None:
        cases = [
            {
                'description': 'Enlarge 4:3 image using same aspect ratio resolution',
                'input_image_shape': (3, 4, 3),
                'resize_resolution': (16, 12),
                'expected_resolution': (16, 12),
            },
            {
                'description': 'Shrink 4:3 image using same aspect ratio resolution',
                'input_image_shape': (768, 1024, 3),
                'resize_resolution': (800, 600),
                'expected_resolution': (800, 600),
            },
            {
                'description': 'Enlarge 4:3 grayscale image using same aspect ratio resolution',
                'input_image_shape': (6, 8),
                'resize_resolution': (80, 60),
                'expected_resolution': (80, 60),
            },
            {
                'description': 'Shrink 16:9 grayscale image using same aspect ratio resolution',
                'input_image_shape': (90, 160),
                'resize_resolution': (80, 45),
                'expected_resolution': (80, 45),
            },
            {
                'description': 'Shrink 9:16 image using same aspect ratio resolution',
                'input_image_shape': (160, 90, 3),
                'resize_resolution': (45, 80),
                'expected_resolution': (45, 80),
            },
            {
                'description': 'Shrink 9:16 image when max width limits the resulting image resolution',
                'input_image_shape': (32, 18, 3),
                'resize_resolution': (9, 24),
                'expected_resolution': (9, 16),
            },
            {
                'description': 'Enlarge 9:16 image when max height limits the resulting image resolution',
                'input_image_shape': (64, 36, 3),
                'resize_resolution': (1000, 72),
                'expected_resolution': (40, 72),
            },
            {
                'description': 'Enlarge 1:1 aspect ratio image #1',
                'input_image_shape': (11, 11, 3),
                'resize_resolution': (110, 110),
                'expected_resolution': (110, 110),
            },
            {
                'description': 'Enlarge 1:1 aspect ratio image #2',
                'input_image_shape': (10, 10, 3),
                'resize_resolution': (100, 1000),
                'expected_resolution': (100, 100),
            },
            {
                'description': 'Enlarge 1:1 aspect ratio image #3',
                'input_image_shape': (3, 3, 3),
                'resize_resolution': (300, 30),
                'expected_resolution': (30, 30),
            },
            {
                'description': 'Shrink 1:1 aspect ratio image #1',
                'input_image_shape': (10, 10, 3),
                'resize_resolution': (1, 1),
                'expected_resolution': (1, 1),
            },
            {
                'description': 'Shrink 1:1 aspect ratio image #2',
                'input_image_shape': (9, 9, 3),
                'resize_resolution': (4, 2),
                'expected_resolution': (2, 2),
            },
            {
                'description': 'Shrink 1:1 aspect ratio image #3',
                'input_image_shape': (8, 8, 3),
                'resize_resolution': (3, 6),
                'expected_resolution': (3, 3),
            },
        ]

        for case in cases:
            with self.subTest(case['description']):
                input_image = numpy.full(
                    case['input_image_shape'],
                    0xff,
                    dtype=numpy.uint8
                )

                img = image.Image(input_image).resize_keeping_aspect_ratio(*case['resize_resolution'])

                expected_image_shape = case['expected_resolution'][::-1]

                if len(case['input_image_shape']) == 3:
                    expected_image_shape += (case['input_image_shape'][2],)

                self.assertTupleEqual(
                    self.get_image_shape(img),
                    expected_image_shape
                )

    def test_add_padding(self) -> None:
        cases = [
            {
                'description': 'Add horizontal padding to image',
                'input_image_data': [
                    [[0xff, 0xff, 0xff]]
                ],
                'padding_resolution': (3, 1),
                'expected_image_data': [
                    [[0x00, 0x00, 0x00], [0xff, 0xff, 0xff], [0x00, 0x00, 0x00]]
                ],
            },
            {
                'description': 'Add vertical padding to image',
                'input_image_data': [
                    [[0xff, 0xff, 0xff]]
                ],
                'padding_resolution': (1, 3),
                'expected_image_data': [
                    [[0x00, 0x00, 0x00]],
                    [[0xff, 0xff, 0xff]],
                    [[0x00, 0x00, 0x00]]
                ],
            },
            {
                'description': 'Add both horizontal and vertical padding to image',
                'input_image_data': [
                    [[0xff, 0xff, 0xff]]
                ],
                'padding_resolution': (3, 3),
                'expected_image_data': [
                    [[0x00, 0x00, 0x00], [0x00, 0x00, 0x00], [0x00, 0x00, 0x00]],
                    [[0x00, 0x00, 0x00], [0xff, 0xff, 0xff], [0x00, 0x00, 0x00]],
                    [[0x00, 0x00, 0x00], [0x00, 0x00, 0x00], [0x00, 0x00, 0x00]]
                ],
            },
            {
                'description': 'Add horizontal padding to grayscale image',
                'input_image_data': [
                    [0xff]
                ],
                'padding_resolution': (3, 1),
                'expected_image_data': [
                    [0x00, 0xff, 0x00]
                ],
            },
            {
                'description': 'Add vertical padding to grayscale image',
                'input_image_data': [
                    [0xff]
                ],
                'padding_resolution': (1, 3),
                'expected_image_data': [
                    [0x00],
                    [0xff],
                    [0x00]
                ],
            },
            {
                'description': 'Add both horizontal and vertical padding to grayscale image',
                'input_image_data': [[0xff]],
                'padding_resolution': (3, 3),
                'expected_image_data': [
                    [0x00, 0x00, 0x00],
                    [0x00, 0xff, 0x00],
                    [0x00, 0x00, 0x00]
                ],
            },
            {
                'description': 'Add padding but it is actually not needed',
                'input_image_data': [
                    [[0xff, 0xff, 0xff], [0xff, 0xff, 0xff], [0xff, 0xff, 0xff]],
                    [[0xff, 0xff, 0xff], [0xff, 0xff, 0xff], [0xff, 0xff, 0xff]],
                    [[0xff, 0xff, 0xff], [0xff, 0xff, 0xff], [0xff, 0xff, 0xff]]
                ],
                'padding_resolution': (3, 3),
                'expected_image_data': [
                    [[0xff, 0xff, 0xff], [0xff, 0xff, 0xff], [0xff, 0xff, 0xff]],
                    [[0xff, 0xff, 0xff], [0xff, 0xff, 0xff], [0xff, 0xff, 0xff]],
                    [[0xff, 0xff, 0xff], [0xff, 0xff, 0xff], [0xff, 0xff, 0xff]]
                ],
            },
            {
                'description': 'Add padding to grayscale image but it is actually not needed',
                'input_image_data': [
                    [0xff, 0xff, 0xff],
                    [0xff, 0xff, 0xff],
                    [0xff, 0xff, 0xff]
                ],
                'padding_resolution': (3, 3),
                'expected_image_data': [
                    [0xff, 0xff, 0xff],
                    [0xff, 0xff, 0xff],
                    [0xff, 0xff, 0xff]
                ],
            },
        ]

        for case in cases:
            with self.subTest(case['description']):
                input_image = numpy.array(
                    case['input_image_data'],
                    dtype=numpy.uint8
                )

                img = image.Image(input_image).add_padding(*case['padding_resolution'])

                self.assertListEqual(
                    self.get_image_data(img),
                    case['expected_image_data'],
                )

    def test_apply_4bpp_floyd_steinberg_dithering(self) -> None:
        input_image = numpy.array(
            [
                [[141, 16, 27], [129, 16, 52], [76, 14, 134], [9, 32, 237]],
                [[129, 17, 52], [76, 14, 134], [10, 32, 237], [5, 83, 246]],
                [[76, 14, 134], [9, 32, 237], [5, 84, 246], [1, 131, 254]],
                [[9, 32, 238], [4, 83, 247], [0, 131, 254], [28, 187, 247]]
            ],
            dtype=numpy.uint8
        )

        allowed_pixel_values = [
            0x00,
            0x11,
            0x22,
            0x33,
            0x44,
            0x55,
            0x66,
            0x77,
            0x88,
            0x99,
            0xaa,
            0xbb,
            0xcc,
            0xdd,
            0xee,
            0xff,
        ]

        img = image.Image(input_image).apply_4bpp_floyd_steinberg_dithering()

        self.assertEqual(len(self.get_image_shape(img)), 2)

        pixel_values = [j for i in self.get_image_data(img) for j in i]

        for pixel_value in pixel_values:
            self.assertIn(pixel_value, allowed_pixel_values)

    def test_save_to_bmp_when_wrong_file_extension_provided(self) -> None:
        img = image.Image(numpy.ndarray((1, 1, 3), dtype=numpy.uint8))
        incorrect_bmp_file_path = os.path.join(
            self.test_directory_path,
            'file_name_with_incorrect.extension'
        )

        self.assertRaisesRegex(
            ValueError,
            r"^File name in argument 'file_path' must end in '\.bmp' extension\.$",
            img.save_to_bmp,
            incorrect_bmp_file_path
        )

        self.assertFalse(os.path.exists(incorrect_bmp_file_path))

    def test_save_to_custom_4bpp_image(self) -> None:
        input_image = numpy.array(
            [
                [0xff, 0xff, 0xff, 0xff],
                [0x00, 0x11, 0x22, 0x33],
                [0x44, 0x55, 0x66, 0x77],
                [0x88, 0x99, 0xaa, 0xbb],
                [0xcc, 0xdd, 0xee, 0xff],
                [0x00, 0x00, 0x00, 0x00]
            ],
            dtype=numpy.uint8
        )

        expected_image_file_contents = (
            b'\x04\x00'  # width (on two bytes in little endian): 4
            b'\x06\x00'  # height (on two bytes in little endian): 6
            b'\xff\xff'
            b'\x32\x10'
            b'\x76\x54'
            b'\xba\x98'
            b'\xfe\xdc'
            b'\x00\x00'
        )

        self.assertFalse(os.path.exists(self.four_bits_per_pixel_image_file_path))

        image.Image(input_image).save_to_custom_4bpp_image(
            self.four_bits_per_pixel_image_file_path
        )

        self.assertTrue(os.path.exists(self.four_bits_per_pixel_image_file_path))

        with open(self.four_bits_per_pixel_image_file_path, 'rb') as image_file:
            image_file_contents = image_file.read()

        self.assertEqual(
            image_file_contents,
            expected_image_file_contents
        )

    def test_save_to_custom_4bpp_image_when_image_has_multiple_color_channels(self) -> None:
        img = image.Image(numpy.ndarray((2, 2, 3), dtype=numpy.uint8))

        self.assertRaisesRegex(
            RuntimeError,
            (
                r"^"
                r"Saving images to the custom 4 bits per pixel format can only work with "
                r"images with a single color channel\. "
                r"You must reduce the number of color channels to one to use this function!"
                r"$"
            ),
            img.save_to_custom_4bpp_image,
            self.four_bits_per_pixel_image_file_path
        )

        self.assertFalse(os.path.exists(self.four_bits_per_pixel_image_file_path))

    def test_save_to_custom_4bpp_image_with_an_image_with_odd_number_of_pixels(self) -> None:
        img = image.Image(numpy.ndarray((1, 1), dtype=numpy.uint8))

        self.assertRaisesRegex(
            RuntimeError,
            r"^The number of pixels in image is odd! Images with odd number of pixels cannot be saved\.$",
            img.save_to_custom_4bpp_image,
            self.four_bits_per_pixel_image_file_path
        )

        self.assertFalse(os.path.exists(self.four_bits_per_pixel_image_file_path))

    def test_save_to_custom_4bpp_image_with_too_high_image_resolutions(self) -> None:
        cases = [
            {
                'image_width': 2 ** 16 - 1,
                'image_height': 2 ** 16 - 1,
            },
            {
                'image_width': 1,
                'image_height': 2 ** 16,
            },
            {
                'image_width': 2 ** 16,
                'image_height': 1,
            },
            {
                'image_width': 2 ** 16 - 2,
                'image_height': 2 ** 16,
            },
            {
                'image_width': 2 ** 16,
                'image_height': 2 ** 16 - 2,
            },
        ]

        for case in cases:
            with self.subTest('{}x{}'.format(case['image_width'], case['image_height'])):
                img = image.Image(
                    numpy.empty((case['image_height'], case['image_width']), dtype=numpy.uint8)
                )

                self.assertRaisesRegex(
                    RuntimeError,
                    (
                        r"^Image resolution is too high! "
                        r"Maximum image resolution is 65535x65534 \(or vice versa\)\.$"
                    ),
                    img.save_to_custom_4bpp_image,
                    self.four_bits_per_pixel_image_file_path
                )

                self.assertFalse(os.path.exists(self.four_bits_per_pixel_image_file_path))
