"""
Test suite for account_creation view.
"""
import os
import sys

# allow for relative imports from "app"
sys.path.append(os.getcwd())

import pytest
import time

import requests

from app import constants as appconstants
from app.models import User

from tests.constants import *

def test_add_invited_user(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    db_resource.session.add(user)
    db_resource.session.commit()
     
    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "default"
        }
    )
    assert response.status_code == 204

    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "default",
            "auth_code": appconstants.TEST_AUTH_CODE
       }
    )
    assert response.status_code == 201

def test_add_uninvited_user(db_resource, req_sess):
    user = User(**TEST_NEW_USER)

    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "default"
        }
    )
    assert response.status_code == 403

def test_bad_auth_code(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    db_resource.session.add(user)
    db_resource.session.commit()
     
    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "default"
        }
    )
    assert response.status_code == 204

    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "default",
            "auth_code": "654321"
       }
    )
    assert response.status_code == 403

def test_add_active_user(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    user.account_status = appconstants.ACTIVE_ACCOUNT
    db_resource.session.add(user)
    db_resource.session.commit()
     
    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "default"
        }
    )
    assert response.status_code == 403

def test_add_disabled_user(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    user.account_status = appconstants.DISABLED_ACCOUNT
    db_resource.session.add(user)
    db_resource.session.commit()
     
    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "default"
        }
    )

    assert response.status_code == 403

def test_add_user_bad_phone_number(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    user.phone_number = "1-877-KARS-4-KIDZ"
    db_resource.session.add(user)
    db_resource.session.commit()
     
    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "default"
        }
    )
    assert response.status_code == 400

def test_add_user_short_phone_number(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    user.phone_number = "12345678910"
    db_resource.session.add(user)
    db_resource.session.commit()
    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "default"
       }
    )
    assert response.status_code == 400

def test_add_user_short_username(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    db_resource.session.add(user)
    db_resource.session.commit()
    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "hi",
            "password": TEST_PASSWORD,
            "profile_uri": "default"
       }
    )
    assert response.status_code == 400

def test_add_user_long_username(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    db_resource.session.add(user)
    db_resource.session.commit()
    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "long_username" * 4,
            "password": TEST_PASSWORD,
            "profile_uri": "default"
       }
    )
    assert response.status_code == 400

def test_add_user_bad_email(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    user.recovery_email = "goofyman.com"
    db_resource.session.add(user)
    db_resource.session.commit()
     
    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "default"
        }
    )
    assert response.status_code == 400


def test_add_user_missing_data(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    db_resource.session.add(user)
    db_resource.session.commit()
    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "profile_uri": "default"
       }
    )
    assert response.status_code == 400

def test_add_user_non_unique_name(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    user.account_status = appconstants.ACTIVE_ACCOUNT
    user.username = "non-unique username"
    db_resource.session.add(user)

    user2 = User(**TEST_NEW_USER_2)
    db_resource.session.add(user2)
    db_resource.session.commit()

    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "non-unique username",
            "password": TEST_PASSWORD,
            "profile_uri": "default"
       }
    )
    assert response.status_code == 400

def test_weak_passwords(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    db_resource.session.add(user)
    db_resource.session.commit()

    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": "pa$$word",
            "profile_uri": "default"
       }
    )
    assert response.status_code == 400

    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": "A$$word",
            "profile_uri": "default"
       }
    )
    assert response.status_code == 400

    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": "Password",
            "profile_uri": "default"
       }
    )
    assert response.status_code == 400

    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": "Pa$$word★",
            "profile_uri": "default"
       }
    )
    assert response.status_code == 400

def test_add_bad_profile(db_resource, req_sess):
    user = User(**TEST_NEW_USER)
    db_resource.session.add(user)
    db_resource.session.commit()
     
    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "nonexistent"
        }
    )
    assert response.status_code == 400

    response = req_sess.post(
        f"{BASE_URL}/create-account",
        json={
            "phone_number": user.phone_number,
            "recovery_email": user.recovery_email,
            "username": "test user",
            "password": TEST_PASSWORD,
            "profile_uri": "default/../../passwd"
        }
    )
    assert response.status_code == 400
