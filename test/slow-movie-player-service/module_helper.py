import importlib.util
import os
import sys
from types import ModuleType


def get_module_from_file(file_path: str) -> ModuleType:
    module_name = os.path.basename(os.path.splitext(file_path)[0])

    if module_name in sys.modules:
        return sys.modules[module_name]

    if not os.path.isabs(file_path):
        file_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            file_path
        )

    spec = importlib.util.spec_from_file_location(module_name, file_path)

    if spec is None:
        raise RuntimeError("Cannot get ModuleSpec from path '{}'!".format(file_path))

    if spec.loader is None:
        raise RuntimeError("ModuleSpec ('{}') has no loader!".format(spec.name))

    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module
