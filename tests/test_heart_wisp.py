"""
Test suite for heart_wisp endpoint.
"""
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

def test_heart_wisp(test_wisp, user_sess, user_2_sess):
    response = user_2_sess.post(
        f"{BASE_URL}/heart-wisp",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200
    response = user_2_sess.get(
        f"{BASE_URL}/hearted-wisps"
    )
    assert response.json()["wisp_ids"][0] == test_wisp["wisp_id"]
    response = user_sess.get(
        f"{BASE_URL}/get-account-info"
    )
    assert response.json()["heartscore"] == 1

def test_self_heart_wisp(test_wisp, user_sess):
    response = user_sess.post(
        f"{BASE_URL}/heart-wisp",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200
    response = user_sess.get(
        f"{BASE_URL}/hearted-wisps"
    )
    assert len(response.json()["wisp_ids"]) == 0
    response = user_sess.get(
        f"{BASE_URL}/get-account-info"
    )
    assert response.json()["heartscore"] == 0


def test_double_heart_wisp(test_wisp, user_sess, user_2_sess):
    response = user_2_sess.post(
        f"{BASE_URL}/heart-wisp",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200
    response = user_2_sess.post(
        f"{BASE_URL}/heart-wisp",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200
    response = user_2_sess.get(
        f"{BASE_URL}/hearted-wisps"
    )
    assert response.json()["wisp_ids"][0] == test_wisp["wisp_id"]
    response = user_sess.get(
        f"{BASE_URL}/get-account-info"
    )
    assert response.json()["heartscore"] == 1

def test_unheart_wisp(test_wisp, user_sess, user_2_sess):
    response = user_2_sess.post(
        f"{BASE_URL}/heart-wisp",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200
    response = user_2_sess.get(
        f"{BASE_URL}/hearted-wisps"
    )
    assert response.json()["wisp_ids"][0] == test_wisp["wisp_id"]
    
    response = user_2_sess.post(
        f"{BASE_URL}/unheart-wisp",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200
    response = user_2_sess.get(
        f"{BASE_URL}/hearted-wisps"
    )
    assert response.status_code == 200
    assert len(response.json()["wisp_ids"]) == 0
    response = user_sess.get(
        f"{BASE_URL}/get-account-info"
    )
    assert response.json()["heartscore"] == 0

def test_blocked_user_heart(test_wisp, test_wisp_2, user_sess, user_2_sess):
    response = user_2_sess.post(
        f"{BASE_URL}/heart-wisp",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200
    response = user_2_sess.get(
        f"{BASE_URL}/hearted-wisps"
    )
    assert response.json()["wisp_ids"][0] == test_wisp["wisp_id"]
    
    response = user_sess.post(
        f"{BASE_URL}/heart-wisp",
        json={"wisp_id": test_wisp_2["wisp_id"]}
    )
    assert response.status_code == 200
    response = user_sess.get(
        f"{BASE_URL}/hearted-wisps"
    )
    assert response.json()["wisp_ids"][0] == test_wisp_2["wisp_id"]
    
    response = user_sess.post(
        f"{BASE_URL}/block-account",
        json={"wisp_id": test_wisp_2["wisp_id"]}
    )
    assert response.status_code == 200
    
    response = user_sess.get(
        f"{BASE_URL}/hearted-wisps"
    )
    assert len(response.json()["wisp_ids"]) == 0
    response = user_2_sess.get(
        f"{BASE_URL}/hearted-wisps"
    )
    assert len(response.json()["wisp_ids"]) == 0
    response = user_sess.get(
        f"{BASE_URL}/get-account-info"
    )
    assert response.json()["heartscore"] == 0

    response = user_2_sess.get(
        f"{BASE_URL}/get-account-info"
    )
    assert response.json()["heartscore"] == 0

