#!/usr/bin/env python3

import grayscalemethod_test
import skip_test
import video_test
import unittest

if __name__ == '__main__':
    test_suite = unittest.TestSuite()
    test_modules = [
        grayscalemethod_test,
        skip_test,
        video_test,
    ]

    for test_module in test_modules:
        test_suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_module))

    unittest.TextTestRunner(verbosity=2).run(test_suite)
