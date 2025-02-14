"""
Test suite for account_blockendpoint.
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

def test_block_wisps(user_sess, user_2_sess):
    NUM_TEST_WISPS = 5
    user_1_wisps = [f"user 1 wisp {i}" for i in range(NUM_TEST_WISPS)]
    user_2_wisps = [f"user 2 wisp {i}" for i in range(NUM_TEST_WISPS)]
    wisp_texts = [val for pair in zip(user_1_wisps, user_2_wisps) for val in pair]
    for i in range(NUM_TEST_WISPS):
        response = user_sess.post(
            f"{BASE_URL}/post-wisp",
            json={"text": user_1_wisps[i]}
        )
        assert response.status_code == 201

        response = user_2_sess.post(
            f"{BASE_URL}/post-wisp",
            json={"text": user_2_wisps[i]}
        )
        assert response.status_code == 201
    
    for sess in [user_sess, user_2_sess]:
        response = sess.get(
            f"{BASE_URL}/get-wisps"
        )
        assert response.status_code == 200
        wisps = response.json()["wisps"]
        assert (len(wisps) == NUM_TEST_WISPS * 2 and
            wisps[0]["text"] == wisp_texts[-1])
    
        for i in range(NUM_TEST_WISPS):
            response = sess.get(
                f"{BASE_URL}/get-wisps",
                params={"newest_wisp_id": wisps[i]["wisp_id"]}
            )
            assert response.status_code == 200
            newer_wisps = response.json()["wisps"]
            assert len(newer_wisps) == i
            if len(newer_wisps):
                assert newer_wisps[0] == wisps[0]
            
            response = sess.get(
                f"{BASE_URL}/get-wisps",
                params={"oldest_wisp_id": wisps[i]["wisp_id"]}
            )
            assert response.status_code == 200
            older_wisps = response.json()["wisps"]
            assert len(older_wisps) == (NUM_TEST_WISPS * 2) - 1 - i
            if len(older_wisps):
                assert older_wisps[0] == wisps[i + 1]

    response = user_sess.post(
        f"{BASE_URL}/block-account",
        json={"wisp_id": wisps[0]["wisp_id"]}
    )
    assert response.status_code == 200

    for sess in [user_sess, user_2_sess]:
        response = sess.get(
            f"{BASE_URL}/get-wisps"
        )
        assert response.status_code == 200
        wisps = response.json()["wisps"]
        print(wisps)
        assert (len(wisps) == NUM_TEST_WISPS)

def test_self_block(user_sess, test_wisp):
    response = user_sess.post(
        f"{BASE_URL}/block-account",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert (response.status_code == 400 and 
        response.json()["error"] == "users cannot block themselves")

def test_unauthenticated_block(req_sess, test_wisp):
    response = req_sess.post(
        f"{BASE_URL}/block-account",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 401

def test_block_to_ban(req_sess, user_sess, test_wisp, 
                      user_2_sess, user_3_sess):
    response = user_2_sess.post(
        f"{BASE_URL}/block-account",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200
    response = user_3_sess.post(
        f"{BASE_URL}/block-account",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200

    wisps = req_sess.get(
        f"{BASE_URL}/get-wisps"
    ).json()["wisps"]
    assert len(wisps) == 0

    response = user_sess.post(
        f"{BASE_URL}/post-wisp",
        json=TEST_WISP
    )
    assert response.status_code == 401

    response = user_sess.get(
        f"{BASE_URL}/get-account-info"
    )
    assert response.status_code == 401

def test_mutual_block(user_sess, test_wisp, user_2_sess, test_wisp_2):
    response = user_2_sess.post(
        f"{BASE_URL}/block-account",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200
    
    response = user_sess.post(
        f"{BASE_URL}/block-account",
        json={"wisp_id": test_wisp_2["wisp_id"]}
    )
    assert response.status_code == 200
