"""
Test suite for account_info view.
"""
import os
import sys

# allow for relative imports from "app"
sys.path.append(os.getcwd())

import pytest

from app import constants as appconstants

from tests.constants import *

def test_account_info(test_user, user_sess):
    response = user_sess.get(
        f"{BASE_URL}/get-account-info"
    )
    assert response.status_code == 200 
    resp_obj = response.json()
    assert all([
        resp_obj[key] == TEST_USER.get(key, 0)
        for key in resp_obj.keys()])

def test_account_unauthenticated(test_user, req_sess):
    response = req_sess.get(
        f"{BASE_URL}/get-account-info"
    )
    assert response.status_code == 401
