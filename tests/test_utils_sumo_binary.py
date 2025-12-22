import os
import sys
from unittest.mock import patch


# Add src to path so imports work without installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from utils.sumo import find_sumo_binary


def test_find_sumo_binary_not_found() -> None:
    with (
        patch("utils.sumo.sumolib.checkBinary", side_effect=Exception("no sumo")),
        patch("utils.sumo.shutil.which", return_value=None),
    ):
        assert find_sumo_binary("sumo") is None


def test_find_sumo_binary_found_absolute() -> None:
    with (
        patch("utils.sumo.sumolib.checkBinary", return_value="/usr/bin/sumo"),
        patch("utils.sumo.shutil.which", return_value=None),
    ):
        assert find_sumo_binary("sumo") == "/usr/bin/sumo"


def test_find_sumo_binary_checkbinary_returns_name() -> None:
    with (
        patch("utils.sumo.sumolib.checkBinary", return_value="sumo"),
        patch("utils.sumo.shutil.which", return_value=None),
    ):
        assert find_sumo_binary("sumo") is None

