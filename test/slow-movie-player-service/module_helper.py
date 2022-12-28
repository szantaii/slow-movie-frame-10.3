import importlib.util
import os
import sys
from types import ModuleType


def get_module_from_file(file_path: str) -> ModuleType:
    module_name = os.path.basename(os.path.splitext(file_path)[0])

    if os.path.isabs(file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
    else:
        current_directory = os.path.dirname(os.path.realpath(__file__))
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(current_directory, file_path))

    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module
