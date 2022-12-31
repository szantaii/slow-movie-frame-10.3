#!/usr/bin/env python3

from unit import configuration_test as configuration_unit_test
from unit import display_test as display_unit_test
from unit import grayscalemethod_test as grayscalemethod_unit_test
from unit import skip_test as skip_unit_test
from unit import video_test as video_unit_test
from functional import configuration_test as configuration_functional_test
from types import ModuleType
import unittest


class TestRunner:
    def __init__(self) -> None:
        self.__test_modules: list[ModuleType] = []
        self.__test_suite: unittest.TestSuite = unittest.TestSuite()

    def add_test_module(self, test_module: ModuleType) -> None:
        if test_module not in self.__test_modules:
            self.__test_modules.append(test_module)

    def add_test_modules(self, test_modules: list[ModuleType]) -> None:
        for test_module in test_modules:
            self.add_test_module(test_module)

    def run(self) -> None:
        for test_module in self.__test_modules:
            self.__test_suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(test_module)
            )

        unittest.TextTestRunner(verbosity=2).run(self.__test_suite)


if __name__ == '__main__':
    unit_test_modules = [
        configuration_unit_test,
        display_unit_test,
        grayscalemethod_unit_test,
        skip_unit_test,
        video_unit_test,
    ]
    functional_test_modules = [
        configuration_functional_test,
    ]

    test_runner = TestRunner()
    test_runner.add_test_modules(unit_test_modules)
    test_runner.add_test_modules(functional_test_modules)
    test_runner.run()
