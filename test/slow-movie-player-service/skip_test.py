from module_helper import get_module_from_file
import sys
import re
from unittest import TestCase

skip = get_module_from_file('../../src/slow-movie-player-service/skip.py')


class AbstractSkipTest(TestCase):
    def test_abstract_skip_is_not_instantiable(self) -> None:
        test_inputs = [
            None,
            True,
            False,
            -1,
            0,
            1,
            -0.000000001,
            0.0,
            1.0,
            float('-inf'),
            float('inf'),
            '',
            'test',
            (),
            ('',),
            ('test str',),
            ('test', 'str'),
            [],
            [''],
            ['test'],
            ['test', 'again'],
        ]

        for test_input in test_inputs:
            with self.subTest(test_input):
                self.assertRaisesRegex(
                    TypeError,
                    r'^Cannot instantiate abstract class\.$',
                    skip.AbstractSkip,
                    test_input
                )


class FrameSkipTest(TestCase):
    def test_frame_skip(self) -> None:
        positive_integers = [
            1,
            2,
            3,
            5,
            7,
            11,
            13,
            17,
            19,
            23,
            29,
            100,
            1000,
            1000000,
            1000000000,
            1000000000000,
            int(sys.float_info.max),
        ]

        for positive_integer in positive_integers:
            with self.subTest(positive_integer):
                frame_skip = skip.FrameSkip(positive_integer)

                self.assertEqual(frame_skip.amount, positive_integer)

    def test_frame_skip_with_non_positive_integers(self) -> None:
        non_positive_integers = [
            0,
            -1,
            -10,
            -100,
            -1000,
            -1000000,
            -1000000000,
            -1000000000000,
            -1 * int(sys.float_info.max),
        ]

        for non_positive_integer in non_positive_integers:
            with self.subTest(non_positive_integer):
                self.assertRaisesRegex(
                    ValueError,
                    r"^Field 'amount' must have a positive value, but value '{}' was provided\.$".format(
                        non_positive_integer
                    ),
                    skip.FrameSkip,
                    non_positive_integer
                )

    def test_frame_skip_with_wrong_types(self) -> None:
        wrong_type_inputs = [
            None,
            0.0,
            1.0,
            -1 * sys.float_info.epsilon,
            sys.float_info.epsilon,
            -1 * sys.float_info.min,
            sys.float_info.min,
            -1 * sys.float_info.max,
            sys.float_info.max,
            float('-inf'),
            float('inf'),
            '',
            'test',
            (),
            ('',),
            ('test str',),
            ('test', 'str'),
            [],
            [''],
            ['test'],
            ['test', 'again'],
        ]

        for wrong_type_input in wrong_type_inputs:
            with self.subTest(wrong_type_input):
                wrong_type = type(wrong_type_input)

                self.assertRaisesRegex(
                    TypeError,
                    r"^Field 'amount' is of type '{}', but should be of type '<class 'int'>' instead\.$".format(
                        wrong_type
                    ),
                    skip.FrameSkip,
                    wrong_type_input
                )


class TimeSkipTest(TestCase):
    def test_time_skip(self) -> None:
        positive_floats = [
            sys.float_info.epsilon,
            sys.float_info.min,
            sys.float_info.max,
            float('inf'),
        ]

        for positive_float in positive_floats:
            with self.subTest(positive_float):
                time_skip = skip.TimeSkip(positive_float)

                self.assertEqual(time_skip.amount, positive_float)

    def test_time_skip_with_non_positive_floats(self) -> None:
        non_positive_floats = [
            0.0,
            -1 * sys.float_info.epsilon,
            -1 * sys.float_info.min,
            -1 * sys.float_info.max,
            float('-inf'),
        ]

        for non_positive_float in non_positive_floats:
            with self.subTest(non_positive_float):
                self.assertRaisesRegex(
                    ValueError,
                    r"^Field 'amount' must have a positive value, but value '{}' was provided\.$".format(
                        re.escape(str(non_positive_float))
                    ),
                    skip.TimeSkip,
                    non_positive_float
                )

    def test_time_skip_with_wrong_types(self) -> None:
        wrong_type_inputs = [
            None,
            True,
            False,
            0,
            1,
            -1,
            int(sys.float_info.max),
            -1 * int(sys.float_info.max),
            '',
            'test',
            (),
            ('',),
            ('test str',),
            ('test', 'str'),
            [],
            [''],
            ['test'],
            ['test', 'again'],
        ]

        for wrong_type_input in wrong_type_inputs:
            with self.subTest(wrong_type_input):
                wrong_type = type(wrong_type_input)

                self.assertRaisesRegex(
                    TypeError,
                    r"^Field 'amount' is of type '{}', but should be of type '<class 'float'>' instead\.$".format(
                        wrong_type
                    ),
                    skip.TimeSkip,
                    wrong_type_input
                )
