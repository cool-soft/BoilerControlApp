import pytest
import sys
import os

SRC_PATH = "app"


@pytest.fixture(scope="session", autouse=True)
def add_src_path_to_modules_path():
    abs_src_path = os.path.abspath(SRC_PATH)
    if abs_src_path not in sys.path:
        sys.path.append(abs_src_path)
