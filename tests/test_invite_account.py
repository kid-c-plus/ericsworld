"""
Test suite for account_invitation view.
"""
import os
import sys
import copy
from sqlalchemy.orm import sessionmaker

# allow for relative imports from "app"
sys.path.append(os.getcwd())

import pytest
import time

import requests

from app import db, appconfig
from app import constants as appconstants
from app.models import User

from tests.constants import *

def test_successful_invite(user_sess):
    number = TEST_NEW_USER["phone_number"]
    resp = user_sess.post(
        f"{BASE_URL}/invite-account",
        json={
            "invited_number": number
        }
    )
    assert (resp.status_code == 200 and User.query.filter_by(
        phone_number=number).first() is not None)

def test_unauthorized_invite(req_sess, test_user):
    number = TEST_NEW_USER["phone_number"]
    resp = req_sess.post(
        f"{BASE_URL}/invite-account",
        json={
            "invited_number": number
        }
    )
    assert (resp.status_code == 401 and User.query.filter_by(
        phone_number=number).first() is None)

def test_existing_user_invite(user_sess):
    user_2 = User(**TEST_USER_2)
    user_2.set_password(TEST_PASSWORD)
    db.session.add(user_2)
    db.session.commit()
    resp = user_sess.post(
        f"{BASE_URL}/invite-account",
        json={
            "invited_number": user_2.phone_number
        }
    )
    assert (resp.status_code == 200 and User.query.filter_by(
            phone_number=user_2.phone_number
        ).first().account_status == appconstants.ACTIVE_ACCOUNT)

def test_max_invites(db_resource, test_user, user_sess):
    for i in range(appconfig["MAX_INVITES"]):
        number = "+1" + ("0" * 12 + str(i))[-12:]
        resp = user_sess.post(
            f"{BASE_URL}/invite-account",
            json={
                "invited_number": number
            }
        )
        assert resp.status_code == 200
    number = TEST_NEW_USER["phone_number"]
    resp = user_sess.post(
        f"{BASE_URL}/invite-account",
        json={
            "invited_number": number
        }
    )
    assert (resp.status_code == 403 and User.query.filter_by(
        phone_number=number).first() is None)


def test_bad_number(user_sess):
    number = "123456789"
    resp = user_sess.post(
        f"{BASE_URL}/invite-account",
        json={
            "invited_number": number
        }
    )
    assert (resp.status_code == 400 and User.query.filter_by(
        phone_number=number).first() is None)
