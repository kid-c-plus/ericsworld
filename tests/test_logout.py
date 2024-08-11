"""
Test suite for logout view. 
"""
import os
import sys
import copy

# allow for relative imports from "app"
sys.path.append(os.getcwd())

import pytest
import time

import requests

from app import constants as appconstants

from tests import constants as testconstants

def test_successful_logout(user_sess):
    response = user_sess.post(f"{testconstants.BASE_URL}/logout")
    assert response.status_code == 200

def test_unauthenticated_logout(req_sess):
    response = req_sess.post(f"{testconstants.BASE_URL}/logout")
    assert response.status_code == 401

def test_tokenless_logout(user_sess):
    user_sess.headers.pop("X-CSRFToken")
    response = user_sess.post(f"{testconstants.BASE_URL}/logout")
    assert response.status_code == 400
