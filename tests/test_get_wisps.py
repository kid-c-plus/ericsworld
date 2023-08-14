"""
Test suite for get_wisps endpoint.
"""
import os
import sys

# allow for relative imports from "app"
sys.path.append(os.getcwd())

import pytest
import time

from app import constants as appconstants
from app import appconfig
from app.models import User

from tests.constants import *

def test_get_wisps(user_sess, test_wisp):
    response = user_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    assert response.status_code == 200
    wisps = response.json()
    assert wisps[0]["text"] == test_wisp["text"]

