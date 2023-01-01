from module_helper import get_module_from_file
from unittest import TestCase
from unittest.mock import call, Mock, mock_open, patch
import numpy

image = get_module_from_file('../../src/slow-movie-player-service/image.py')


class ImageTest(TestCase):
    @patch('numpy.uint8')
    @patch('numpy.ndarray', spec=numpy.ndarray)
    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_custom_4bpp_image_with_too_high_image_resolutions(
        self,
        open_function_mock: Mock,
        numpy_ndarray_mock: Mock,
        numpy_uint8_mock: Mock
    ) -> None:

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
                input_image_mock = numpy_ndarray_mock(
                    (case['image_height'], case['image_width']),
                    dtype=numpy_uint8_mock
                )
                input_image_mock.dtype.__ne__.return_value = False
                input_image_mock.shape = case['image_height'], case['image_width']

                open_function_mock.reset_mock()
                numpy_ndarray_mock.reset_mock()
                numpy_uint8_mock.reset_mock()
                input_image_mock.reset_mock()

                expected_open_function_mock_calls = [
                    call(image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[0], 'w'),
                    call().__enter__(),
                    call().write(image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[1]),
                    call().__exit__(None, None, None),
                ]
                expected_numpy_ndarray_mock_calls = [
                     call().dtype.__ne__(numpy_uint8_mock),
                ]
                expected_input_image_mock_calls = [
                    call.dtype.__ne__(numpy_uint8_mock),
                ]

                self.assertListEqual(open_function_mock.mock_calls, [])
                self.assertListEqual(numpy_ndarray_mock.mock_calls, [])
                self.assertListEqual(numpy_uint8_mock.mock_calls, [])
                self.assertListEqual(input_image_mock.mock_calls, [])

                img = image.Image(input_image_mock)

                self.assertRaisesRegex(
                    RuntimeError,
                    (
                        r"^Image resolution is too high! "
                        r"Maximum image resolution is 65535x65534 \(or vice versa\)\.$"
                    ),
                    img.save_to_custom_4bpp_image,
                    '/this/image/file/should/not/be/written.4bpp'
                )

                self.assertListEqual(open_function_mock.mock_calls, expected_open_function_mock_calls)
                self.assertListEqual(numpy_ndarray_mock.mock_calls, expected_numpy_ndarray_mock_calls)
                self.assertListEqual(numpy_uint8_mock.mock_calls, [])
                self.assertListEqual(input_image_mock.mock_calls, expected_input_image_mock_calls)
