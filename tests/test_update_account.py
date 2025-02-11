"""
Tests for account update view.
"""
import os
import sys
import copy

# allow for relative imports from "app"
sys.path.append(os.getcwd())

import pytest
import time

import requests

from app import db, appconfig
from app import constants as appconstants
from app.models import User

from tests.constants import *

"""
def test_update_number(user_sess):
    response = user_sess.post(
            f"{BASE_URL}/update-number",
            json={
                "new_number": TEST_USER_2["phone_number"],
                "password": TEST_PASSWORD
            }
    )
    assert response.status_code == 204

    response = user_sess.post(
            f"{BASE_URL}/update-number",
            json={
                "new_number": TEST_USER_2["phone_number"],
                "password": TEST_PASSWORD,
                "auth_code": appconstants.TEST_AUTH_CODE
            }
    )
    assert (response.status_code == 200 and User.query.filter_by(
            phone_number=TEST_USER_2["phone_number"]
        ).first() is not None)

def test_bad_number(user_sess):
    bad_number = "123456abcdef"
    response = user_sess.post(
            f"{BASE_URL}/update-number",
            json={
                "new_number": bad_number,
                "password": TEST_PASSWORD
            }
    )
    assert (response.status_code == 400 and User.query.filter_by(
            phone_number=bad_number
        ).first() is None)

def test_number_bad_password(user_sess):
    response = user_sess.post(
            f"{BASE_URL}/update-number",
            json={
                "new_number": TEST_USER_2["phone_number"],
                "password": "bad_password"
            }
    )
    assert (response.status_code == 403 and User.query.filter_by(
            phone_number=TEST_USER_2["phone_number"]
        ).first() is None)

def test_number_bad_auth(user_sess):
    response = user_sess.post(
            f"{BASE_URL}/update-number",
            json={
                "new_number": TEST_USER_2["phone_number"],
                "password": TEST_PASSWORD
            }
    )
    assert response.status_code == 204

    response = user_sess.post(
            f"{BASE_URL}/update-number",
            json={
                "new_number": TEST_USER_2["phone_number"],
                "password": TEST_PASSWORD,
                "auth_code": "9999"
            }
    )
    assert (response.status_code == 403 and User.query.filter_by(
            phone_number=TEST_USER_2["phone_number"]
        ).first() is None)

def test_number_in_use(user_sess, test_user_2):
    response = user_sess.post(
                f"{BASE_URL}/update-number",
                json={
                    "new_number": TEST_USER_2["phone_number"],
                    "password": TEST_PASSWORD
                }
    )
    assert response.status_code == 400

def test_update_email(test_user, db_resource, user_sess):
    response = user_sess.post(
            f"{BASE_URL}/update-recovery-email",
            json={
                "new_email": TEST_USER_2["recovery_email"],
                "password": TEST_PASSWORD
            }
    )
    assert (response.status_code == 200 and User.query.filter_by(
            phone_number=TEST_USER["phone_number"]
        ).first().recovery_email == TEST_USER_2["recovery_email"])

def test_bad_email(user_sess):
    response = user_sess.post(
            f"{BASE_URL}/update-recovery-email",
            json={
                "new_email": "bad_email",
                "password": TEST_PASSWORD
            }
    )
    assert (response.status_code == 400 and User.query.filter_by(
            phone_number=TEST_USER["phone_number"]
        ).first().recovery_email == TEST_USER["recovery_email"])

def test_email_bad_password(user_sess):
    response = user_sess.post(
            f"{BASE_URL}/update-recovery-email",
            json={
                "new_email": TEST_USER_2["recovery_email"],
                "password": "bad_password"
            }
    )
    assert (response.status_code == 403 and User.query.filter_by(
            phone_number=TEST_USER["phone_number"]
        ).first().recovery_email == TEST_USER["recovery_email"])

def test_update_password(db_resource, user_sess):
    response = user_sess.post(
            f"{BASE_URL}/update-password",
            json={
                "current_password": TEST_PASSWORD,
                "new_password": TEST_PASSWORD_2
            }
    )
    assert (response.status_code == 200 and db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=TEST_USER["phone_number"]
        )).scalar().check_password(TEST_PASSWORD_2))

def test_update_bad_old_password(db_resource, user_sess):
    response = user_sess.post(
            f"{BASE_URL}/update-password",
            json={
                "current_password": "bad_pass",
                "new_password": TEST_PASSWORD_2
            }
    )
    assert (response.status_code == 403 and db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=TEST_USER["phone_number"]
        )).scalar().check_password(TEST_PASSWORD))

def test_update_bad_new_password(db_resource, user_sess):
    response = user_sess.post(
            f"{BASE_URL}/update-password",
            json={
                "current_password": TEST_PASSWORD,
                "new_password": "bad_pass"
            }
    )
    assert (response.status_code == 400 and db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=TEST_USER["phone_number"]
        )).scalar().check_password(TEST_PASSWORD))

def test_update_username(db_resource, user_sess):
    new_username = "new user :~)"
    response = user_sess.post(
            f"{BASE_URL}/update-username",
            json={
                "new_username": new_username
            }
    )
    assert (response.status_code == 200 and db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=TEST_USER["phone_number"]
        )).scalar().username == new_username)

def test_bad_username(db_resource, user_sess):
    response = user_sess.post(
            f"{BASE_URL}/update-username",
            json={
                "new_username": "long username " * 2
            }
    )
    assert (response.status_code == 400 and db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=TEST_USER["phone_number"]
        )).scalar().username == TEST_USER["username"])


    response = user_sess.post(
            f"{BASE_URL}/update-username",
            json={
                "new_username": "s"
            }
    )
    assert (response.status_code == 400 and db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=TEST_USER["phone_number"]
        )).scalar().username == TEST_USER["username"])

def test_non_unique_username(db_resource, user_sess, test_user_2):
    response = user_sess.post(
            f"{BASE_URL}/update-username",
            json={
                "new_username": TEST_USER_2["username"]
            }
    )
    assert (response.status_code == 400 and db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=TEST_USER["phone_number"]
        )).scalar().username == TEST_USER["username"])

def test_update_profile(db_resource, user_sess):
    new_profile = "default2"
    response = user_sess.post(
            f"{BASE_URL}/update-profile",
            json={
                "new_profile": new_profile
            }
    )
    assert (response.status_code == 200 and db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=TEST_USER["phone_number"]
        )).scalar().profile_uri == new_profile)

def test_nonexistent_profile(db_resource, user_sess):
    response = user_sess.post(
            f"{BASE_URL}/update-profile",
            json={
                "new_profile": "nonexistent_profile"
            }
    )
    assert (response.status_code == 400 and db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=TEST_USER["phone_number"]
        )).scalar().profile_uri == TEST_USER["profile_uri"])

    response = user_sess.post(
            f"{BASE_URL}/update-profile",
            json={
                "new_profile": "../../config.py"
            }
    )
    assert (response.status_code == 400 and db_resource.session.execute(
        db_resource.select(User).filter_by(
            phone_number=TEST_USER["phone_number"]
        )).scalar().profile_uri == TEST_USER["profile_uri"])


"""
def test_get_profiles(user_sess):
    folder = "RICKSPICKS"
    profile = "cowboy.png"
    response = user_sess.get(
        f"{BASE_URL}/get-profiles",
        params={})
    assert response.status_code == 200 and folder in response.json()['folders']
    response = user_sess.get(
        f"{BASE_URL}/get-profiles",
        params={'folder': folder})
    assert response.status_code == 200 and f"{folder}/{profile}" in response.json()['profiles']

