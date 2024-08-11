"""
Test suite for login view. 
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
from app.models import User

from tests import constants as testconstants

def test_successful_login(test_user, req_sess):
    response = req_sess.post(f"{testconstants.BASE_URL}/login", json={
        "phone_number": test_user.phone_number,
        "password": testconstants.TEST_PASSWORD
    })
    assert response.status_code == 200

def test_tokenless_login(test_user):
    response = requests.post(f"{testconstants.BASE_URL}/login", json={
        "phone_number": test_user.phone_number,
        "password": testconstants.TEST_PASSWORD
    })
    assert response.status_code == 400

def test_unsuccessful_login(test_user, req_sess):
    response = req_sess.post(f"{testconstants.BASE_URL}/login", json={
        "phone_number": test_user.phone_number,
        "password": "bad_password"
    })
    assert response.status_code == 403

def test_pwless_login(test_user, req_sess):
    response = req_sess.post(f"{testconstants.BASE_URL}/login", json={
        "phone_number": test_user.phone_number
    })
    assert response.status_code == 400

def test_nonexistent_user_login(db_resource, req_sess):
    response = req_sess.post(f"{testconstants.BASE_URL}/login", json={
        "phone_number": testconstants.TEST_USER["phone_number"],
        "password": testconstants.TEST_PASSWORD
    })
    assert response.status_code == 403


def test_non_active_user_login(db_resource, test_user, req_sess):
    test_user.status = appconstants.DISABLED_USER
    test_user._sa_instance_state.session.commit()
    response = req_sess.post(f"{testconstants.BASE_URL}/login", json={
        "phone_number": test_user.phone_number,
        "password": testconstants.TEST_PASSWORD
    })
    assert response.status_code == 403

    test_user.status = appconstants.INVITED_USER
    db_resource.session.commit()
    response = req_sess.post(f"{testconstants.BASE_URL}/login", json={
        "phone_number": test_user.phone_number,
        "password": testconstants.TEST_PASSWORD
    })
    assert response.status_code == 403
