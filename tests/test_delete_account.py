import os
import sys

# allow for relative imports from "app"
sys.path.append(os.getcwd())

import pytest
import time
import uuid
from datetime import datetime

from sqlalchemy.orm import sessionmaker

from app import constants as appconstants
from app import appconfig
from app.models import *

from tests.constants import *

def test_delete_account(user_sess, test_wisp, user_2_sess):
    response = user_sess.post(
        f"{BASE_URL}/delete-account",
        json={"password": TEST_PASSWORD}
    )
    assert response.status_code == 200
    response = user_sess.get(
        f"{BASE_URL}/get-account-info"
    )
    assert response.status_code == 401
    response = user_2_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    assert len(response.json()["wisps"]) == 0
