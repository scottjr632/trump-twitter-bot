import requests
import logging

import app.definitions as defs


def test_root_dir_exists():
    assert defs.ROOT_DIR != ''

