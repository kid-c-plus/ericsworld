"""
Test suite for account_creation view.
"""
import os
import sys
import copy

# allow for relative imports from "app"
sys.path.append(os.getcwd())

import pytest
import time
from datetime import timedelta

import requests

from app import appconfig
from app import constants as appconstants
from app.models import User

from tests.constants import *

def test_password_reset(db_resource, test_user, req_sess):
    response = req_sess.post(
        f"{BASE_URL}/request-password-reset",
        json={
            "phone_number": test_user.phone_number
        }
    )
    assert response.status_code == 202 and os.path.exists(
        appconstants.RESET_TOKEN_FILE)

    reset_token = open(appconstants.RESET_TOKEN_FILE).read()
    new_password = "new_password"
    response = req_sess.post(
        f"{BASE_URL}/reset-password",
        json={
            "phone_number": test_user.phone_number,
            "reset_token": reset_token,
            "new_password": new_password
        }
    )
    assert response.status_code == 204
    
    response = req_sess.post(
        f"{BASE_URL}/reset-password",
        json={
            "phone_number": test_user.phone_number,
            "reset_token": reset_token,
            "auth_code": appconstants.TEST_AUTH_CODE,
            "new_password": new_password
        }
    )
    assert response.status_code == 200 and db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=test_user.phone_number
        )).scalar().check_password(new_password)


def test_password_reset_too_frequent(db_resource, test_user, req_sess):
    response = req_sess.post(
        f"{BASE_URL}/request-password-reset",
        json={
            "phone_number": test_user.phone_number
        }
    )
    assert response.status_code == 202 and os.path.exists(
        appconstants.RESET_TOKEN_FILE)
    os.remove(appconstants.RESET_TOKEN_FILE)

    response = req_sess.post(
        f"{BASE_URL}/request-password-reset",
        json={
            "phone_number": test_user.phone_number
        }
    )
    assert response.status_code == 202 and not os.path.exists(
        appconstants.RESET_TOKEN_FILE)

def test_password_reset_timeout(db_resource, test_user, req_sess):
    response = req_sess.post(
        f"{BASE_URL}/request-password-reset",
        json={
            "phone_number": test_user.phone_number
        }
    )
    assert response.status_code == 202 and os.path.exists(
        appconstants.RESET_TOKEN_FILE)

    time.sleep(6)
    reset_token = open(appconstants.RESET_TOKEN_FILE).read()
    new_password = "new_password"
    response = req_sess.post(
        f"{BASE_URL}/reset-password",
        json={
            "phone_number": test_user.phone_number,
            "reset_token": reset_token,
            "new_password": new_password
        }
    )
    assert response.status_code == 403

def test_password_reset_bad_password(db_resource, test_user, req_sess):
    response = req_sess.post(
        f"{BASE_URL}/request-password-reset",
        json={
            "phone_number": test_user.phone_number
        }
    )
    assert response.status_code == 202 and os.path.exists(
        appconstants.RESET_TOKEN_FILE)

    reset_token = open(appconstants.RESET_TOKEN_FILE).read()
    new_password = "new_password"
    response = req_sess.post(
        f"{BASE_URL}/reset-password",
        json={
            "phone_number": test_user.phone_number,
            "reset_token": reset_token,
            "new_password": new_password
        }
    )
    assert response.status_code == 204
    
    response = req_sess.post(
        f"{BASE_URL}/reset-password",
        json={
            "phone_number": test_user.phone_number,
            "reset_token": reset_token,
            "auth_code": appconstants.TEST_AUTH_CODE,
            "new_password": "badpass"
        }
    )
    assert response.status_code == 400 and not db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=test_user.phone_number
        )).scalar().check_password(new_password)


def test_password_reset_bad_auth(db_resource, test_user, req_sess):
    response = req_sess.post(
        f"{BASE_URL}/request-password-reset",
        json={
            "phone_number": test_user.phone_number
        }
    )
    assert response.status_code == 202 and os.path.exists(
        appconstants.RESET_TOKEN_FILE)

    reset_token = open(appconstants.RESET_TOKEN_FILE).read()
    new_password = "new_password"
    response = req_sess.post(
        f"{BASE_URL}/reset-password",
        json={
            "phone_number": test_user.phone_number,
            "reset_token": reset_token,
            "new_password": new_password
        }
    )
    assert response.status_code == 204
    
    response = req_sess.post(
        f"{BASE_URL}/reset-password",
        json={
            "phone_number": test_user.phone_number,
            "reset_token": reset_token,
            "auth_code": "8989",
            "new_password": new_password
        }
    )
    assert response.status_code == 403 and not db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=test_user.phone_number
        )).scalar().check_password(new_password)

def test_password_reset_inactive_user(db_resource, test_user, req_sess):
    test_user.status = appconstants.DISABLED_USER
    test_user._sa_instance_state.session.commit()
    response = req_sess.post(
        f"{BASE_URL}/request-password-reset",
        json={
            "phone_number": test_user.phone_number
        }
    )
    assert response.status_code == 202 and not os.path.exists(
        appconstants.RESET_TOKEN_FILE)

    
