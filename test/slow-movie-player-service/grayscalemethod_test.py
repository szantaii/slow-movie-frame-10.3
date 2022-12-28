from module_helper import get_module_from_file
from unittest import TestCase

grayscalemethod = get_module_from_file('../../src/slow-movie-player-service/grayscalemethod.py')


class GrayscaleMethodTest(TestCase):
    def test_grayscale_method_value(self) -> None:
        test_input_expected_value_pairs = {
            'Rec601Luma': 'Rec601Luma',
            'Rec601Luminance': 'Rec601Luminance',
            'Rec709Luma': 'Rec709Luma',
            'Rec709Luminance': 'Rec709Luminance',
            'Brightness': 'Brightness',
            'Lightness': 'Lightness',
            'Average': 'Average',
            'RMS': 'RMS',
            '': 'Rec709Luma',
            'None': 'Rec709Luma',
            'True': 'Rec709Luma',
            'False': 'Rec709Luma',
            '0': 'Rec709Luma',
            '1': 'Rec709Luma',
            '0.0': 'Rec709Luma',
            '-inf': 'Rec709Luma',
            'inf': 'Rec709Luma',
            r"¯\_(ツ)_/¯": 'Rec709Luma',
        }

        for test_input, expected_value in test_input_expected_value_pairs.items():
            with self.subTest(test_input=test_input):
                grayscale_method = grayscalemethod.GrayscaleMethod(test_input)

                self.assertEqual(grayscale_method.value, expected_value)
