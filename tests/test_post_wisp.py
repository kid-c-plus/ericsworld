"""
Test suite for post_wisp view.
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

def test_post_wisp(user_sess):
    response = user_sess.post(
        f"{BASE_URL}/post-wisp",
        json=TEST_WISP
    )
    assert response.status_code == 201

    response = user_sess.post(
        f"{BASE_URL}/post-wisp",
        json={"text": TEST_WISP["text"]}
    )
    assert response.status_code == 201

def test_invalid_wisps(user_sess):
    response = user_sess.post(
        f"{BASE_URL}/post-wisp",
        json={"wisp": "right here :~)"}
    )
    assert response.status_code == 400

    response = user_sess.post(
        f"{BASE_URL}/post-wisp",
        json={
            "text": TEST_WISP["text"],
            "gif_uri": "deadbeef" * 8
        }
    )
    assert response.status_code == 400

    response = user_sess.post(
        f"{BASE_URL}/post-wisp",
        json={
            "text": "a" * (appconfig["MAX_WISP_LENGTH"] + 1)
        }
    )
    assert response.status_code == 400

def test_unauthenticated_wisp(req_sess):
    response = req_sess.post(
        f"{BASE_URL}/post-wisp",
        json=TEST_WISP
    )
    assert response.status_code == 401

def test_sanitize_wisps(user_sess):
    response = user_sess.post(
        f"{BASE_URL}/post-wisp",
        json={
            "text": "hello <span> evil </span> there"
        }
    )
    assert response.status_code == 201

    response = user_sess.post(
        f"{BASE_URL}/post-wisp",
        json={
            "text": "hello <span> evil </span> there",
            "gif_uri": TEST_WISP["gif_uri"] + "../../config.py"
        }
    )
    assert response.status_code == 400

def test_max_wisps(user_sess):
    for _ in range(appconfig["MAX_WISPS_PER_USER"]):
        response = user_sess.post(
            f"{BASE_URL}/post-wisp",
            json=TEST_WISP
        )
        assert response.status_code == 201
    response = user_sess.post(
        f"{BASE_URL}/post-wisp",
        json=TEST_WISP
    )
    assert response.status_code == 403
