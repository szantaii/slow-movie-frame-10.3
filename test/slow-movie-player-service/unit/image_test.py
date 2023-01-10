from module_helper import get_module_from_file
from unittest import TestCase
from unittest.mock import call, Mock, patch
import numpy
import cv2
import tempfile
import subprocess

grayscalemethod = get_module_from_file('../../src/slow-movie-player-service/grayscalemethod.py')
image = get_module_from_file('../../src/slow-movie-player-service/image.py')


class ImageTest(TestCase):
    @patch('os.remove')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen', spec=subprocess.Popen)
    @patch('tempfile.NamedTemporaryFile', spec=tempfile.NamedTemporaryFile)
    @patch('image.GrayscaleMethod', spec=grayscalemethod.GrayscaleMethod)
    @patch('cv2.IMREAD_GRAYSCALE')
    @patch('cv2.imdecode', spec=cv2.imdecode)
    @patch('cv2.imencode', spec=cv2.imencode)
    @patch('numpy.asarray')
    @patch('numpy.uint8')
    @patch('numpy.ndarray', spec=numpy.ndarray)
    def test_palette_file_creation_and_removal_in_apply_4bpp_floyd_steinberg_dithering(
        self,
        numpy_ndarray_mock: Mock,
        numpy_uint8_mock: Mock,
        numpy_asarray_function_mock: Mock,
        cv2_imencode_function_mock: Mock,
        cv2_imdecode_function_mock: Mock,
        cv2_imread_grayscale_option_mock: Mock,
        grayscale_method_mock: Mock,
        named_temp_file_mock: Mock,
        subprocess_popen_mock: Mock,
        subprocess_pipe_mock: Mock,
        os_remove_function_mock: Mock
    ) -> None:
        dummy_ppm_image_data = b'dummy PPM image data'
        dummy_pgm_image_data = b'dummy PGM image data'

        input_image_mock = numpy_ndarray_mock((1404, 1872), dtype=numpy_uint8_mock)
        input_image_mock.dtype.__ne__.return_value = False

        ppm_image_mock = numpy_ndarray_mock((1404, 1872), dtype=numpy_uint8_mock)
        ppm_image_mock.tobytes.return_value = dummy_ppm_image_data

        pgm_image_data_mock = numpy_asarray_function_mock(bytearray(dummy_pgm_image_data), dtype=numpy_uint8_mock)

        cv2_imencode_function_mock.return_value = True, ppm_image_mock

        grayscale_method_mock.value = 'DummyGrayscaleMethod'

        grayscale_palette_file_mock = named_temp_file_mock(
            mode='w',
            encoding='ascii',
            suffix='.{}'.format(image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[0]),
            delete=False
        )
        grayscale_palette_file_mock.name = '/dummy/path/tmp.{}'.format(
            image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[0]
        )

        convert_process_mock = subprocess_popen_mock(
            [
                'convert',
                '-',
                '-grayscale',
                grayscale_method_mock.value,
                '-dither',
                'FloydSteinberg',
                '-remap',
                grayscale_palette_file_mock.name,
                'pgm:-'
            ],
            stdin=subprocess_pipe_mock,
            stdout=subprocess_pipe_mock,
            stderr=subprocess_pipe_mock
        )

        convert_process_mock.communicate.return_value = dummy_pgm_image_data, None
        convert_process_mock.returncode = 0

        numpy_ndarray_mock.reset_mock()
        numpy_asarray_function_mock.reset_mock()
        named_temp_file_mock.reset_mock()
        subprocess_popen_mock.reset_mock()

        expected_numpy_ndarray_mock_calls = [
            call().dtype.__ne__(numpy_uint8_mock),
            call().tobytes(),
        ]
        expected_numpy_asarray_function_mock_calls = [
            call(bytearray(dummy_pgm_image_data), dtype=numpy_uint8_mock),
        ]
        expected_cv2_imencode_function_mock_calls = [
            call('.ppm', ppm_image_mock),
        ]
        expected_cv2_imdecode_function_mock_calls = [
            call(pgm_image_data_mock, cv2_imread_grayscale_option_mock),
        ]
        expected_named_temp_file_mock_calls = [
            call(
                mode='w',
                encoding='ascii',
                suffix='.{}'.format(image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[0]),
                delete=False
            ),
            call().write(image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[1]),
            call().close(),
        ]
        expected_subprocess_popen_mock_calls = [
            call(
                [
                    'convert',
                    '-',
                    '-grayscale',
                    grayscale_method_mock.value,
                    '-dither',
                    'FloydSteinberg',
                    '-remap',
                    grayscale_palette_file_mock.name,
                    'pgm:-'
                ],
                stdin=subprocess_pipe_mock,
                stdout=subprocess_pipe_mock,
                stderr=subprocess_pipe_mock
            ),
            call().communicate(input=dummy_ppm_image_data),
        ]
        expected_os_remove_function_mock_calls = [
            call(grayscale_palette_file_mock.name),
        ]
        expected_grayscale_palette_file_mock_calls = [
            call.write(image.Image.SIXTEEN_COLOR_GRAYSCALE_PALETTE_IMAGE[1]),
            call.close(),
        ]
        expected_convert_process_mock_calls = [
            call.communicate(input=dummy_ppm_image_data),
        ]

        self.assertListEqual(numpy_ndarray_mock.mock_calls, [])
        self.assertListEqual(numpy_asarray_function_mock.mock_calls, [])
        self.assertListEqual(cv2_imencode_function_mock.mock_calls, [])
        self.assertListEqual(cv2_imdecode_function_mock.mock_calls, [])
        self.assertListEqual(named_temp_file_mock.mock_calls, [])
        self.assertListEqual(subprocess_popen_mock.mock_calls, [])
        self.assertListEqual(os_remove_function_mock.mock_calls, [])
        self.assertListEqual(grayscale_palette_file_mock.mock_calls, [])
        self.assertListEqual(convert_process_mock.mock_calls, [])

        image.Image(input_image_mock).apply_4bpp_floyd_steinberg_dithering(grayscale_method_mock)

        self.assertListEqual(numpy_ndarray_mock.mock_calls, expected_numpy_ndarray_mock_calls)
        self.assertListEqual(numpy_asarray_function_mock.mock_calls, expected_numpy_asarray_function_mock_calls)
        self.assertListEqual(cv2_imencode_function_mock.mock_calls, expected_cv2_imencode_function_mock_calls)
        self.assertListEqual(cv2_imdecode_function_mock.mock_calls, expected_cv2_imdecode_function_mock_calls)
        self.assertListEqual(named_temp_file_mock.mock_calls, expected_named_temp_file_mock_calls)
        self.assertListEqual(subprocess_popen_mock.mock_calls, expected_subprocess_popen_mock_calls)
        self.assertListEqual(os_remove_function_mock.mock_calls, expected_os_remove_function_mock_calls)
        self.assertListEqual(grayscale_palette_file_mock.mock_calls, expected_grayscale_palette_file_mock_calls)
        self.assertListEqual(convert_process_mock.mock_calls, expected_convert_process_mock_calls)

    @patch('numpy.uint8')
    @patch('numpy.ndarray', spec=numpy.ndarray)
    def test_save_to_custom_4bpp_image_with_too_high_image_resolutions(
        self,
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

                numpy_ndarray_mock.reset_mock()
                numpy_uint8_mock.reset_mock()
                input_image_mock.reset_mock()

                expected_numpy_ndarray_mock_calls = [
                     call().dtype.__ne__(numpy_uint8_mock),
                ]
                expected_input_image_mock_calls = [
                    call.dtype.__ne__(numpy_uint8_mock),
                ]

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

                self.assertListEqual(numpy_ndarray_mock.mock_calls, expected_numpy_ndarray_mock_calls)
                self.assertListEqual(numpy_uint8_mock.mock_calls, [])
                self.assertListEqual(input_image_mock.mock_calls, expected_input_image_mock_calls)
