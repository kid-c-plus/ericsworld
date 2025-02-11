"""
Test suite for get_wisps endpoint.
"""
import os
import sys

# allow for relative imports from "app"
sys.path.append(os.getcwd())

import pytest
import time
import uuid
import datetime as dt

from sqlalchemy.orm import Session

from app import constants as appconstants
from app import appconfig
from app.models import *

from tests.constants import *
"""
def test_no_wisps(user_sess):
    response = user_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    assert response.status_code == 200
    wisps = response.json()["wisps"]
    assert len(wisps) == 0

def test_get_wisps(user_sess, test_wisp):
    response = user_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    assert response.status_code == 200
    wisps = response.json()["wisps"]
    assert wisps[0]["text"] == test_wisp["text"]

def test_many_wisps(user_sess):
    response = user_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    assert response.status_code == 200
    wisps = response.json()["wisps"]
    assert len(wisps) == 0
    
    NUM_TEST_WISPS = 10
    wisp_texts = [f"TEST WISP {i}" for i in range(NUM_TEST_WISPS)]
    for text in wisp_texts:
        response = user_sess.post(
            f"{BASE_URL}/post-wisp",
            json={"text": text}
        )
        assert response.status_code == 201

    response = user_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    assert response.status_code == 200
    wisps = response.json()["wisps"]
    assert (len(wisps) == NUM_TEST_WISPS and
        wisps[0]["text"] == wisp_texts[-1])
    
    for i in range(NUM_TEST_WISPS):
        response = user_sess.get(
            f"{BASE_URL}/get-wisps",
            params={"newest_wisp_id": wisps[i]["wisp_id"]}
        )
        assert response.status_code == 200
        newer_wisps = response.json()["wisps"]
        assert len(newer_wisps) == i
        if len(newer_wisps):
            assert newer_wisps[0] == wisps[0]
        
        response = user_sess.get(
            f"{BASE_URL}/get-wisps",
            params={"oldest_wisp_id": wisps[i]["wisp_id"]}
        )
        assert response.status_code == 200
        older_wisps = response.json()["wisps"]
        assert len(older_wisps) == NUM_TEST_WISPS - 1 - i
        if len(older_wisps):
            assert older_wisps[0] == wisps[i + 1]

def test_simultaneous_wisps(db_resource, test_user, user_sess):
    NUM_TEST_WISPS = 10
    wisp_texts = [f"TEST WISP {i}" for i in range(NUM_TEST_WISPS)]
    created_time = dt.datetime.now(dt.UTC)
    for text in wisp_texts:
        wisp = Wisp(
            wisp_id=uuid.uuid1().hex,
            created_time=created_time,
            user=test_user,
            text=text
        )
        session = Session.object_session(test_user)
        session.add(wisp)
        session.commit()
    time.sleep(0.5)
    response = user_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    assert response.status_code == 200
    wisps = response.json()["wisps"]
    assert len(wisps) == NUM_TEST_WISPS

    for i in range(NUM_TEST_WISPS):
        response = user_sess.get(
            f"{BASE_URL}/get-wisps",
            params={"newest_wisp_id": wisps[i]["wisp_id"]}
        )
        assert response.status_code == 200
        newer_wisps = response.json()["wisps"]
        assert len(newer_wisps) == i
        if len(newer_wisps):
            assert newer_wisps[0] == wisps[0]
        
        response = user_sess.get(
            f"{BASE_URL}/get-wisps",
            params={"oldest_wisp_id": wisps[i]["wisp_id"]}
        )
        assert response.status_code == 200
        older_wisps = response.json()["wisps"]
        assert len(older_wisps) == NUM_TEST_WISPS - 1 - i
        if len(older_wisps):
            assert older_wisps[0] == wisps[i + 1]
        
def test_anonymous_wisp(user_sess, req_sess):
    NUM_TEST_WISPS = 10
    wisp_texts = [f"TEST WISP {i}" for i in range(NUM_TEST_WISPS)]
    for text in wisp_texts:
        response = user_sess.post(
            f"{BASE_URL}/post-wisp",
            json={"text": text}
        )
        assert response.status_code == 201

    response = req_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    assert response.status_code == 200
    wisps = response.json()["wisps"]
    assert (len(wisps) == appconfig["MAX_WISPS_PER_USER"] and
        wisps[0]["text"] == wisp_texts[-1])
    
    for i in range(NUM_TEST_WISPS):
        response = req_sess.get(
            f"{BASE_URL}/get-wisps",
            params={"newest_wisp_id": wisps[i]["wisp_id"]}
        )
        assert response.status_code == 200
        newer_wisps = response.json()["wisps"]
        assert len(newer_wisps) == i
        if len(newer_wisps):
            assert newer_wisps[0] == wisps[0]
        
        response = req_sess.get(
            f"{BASE_URL}/get-wisps",
            params={"oldest_wisp_id": wisps[i]["wisp_id"]}
        )
        assert response.status_code == 200
        older_wisps = response.json()["wisps"]
        assert len(older_wisps) == NUM_TEST_WISPS - 1 - i
        if len(older_wisps):
            assert older_wisps[0] == wisps[i + 1]
        
def test_check_newest_wisp(user_sess):
    response = user_sess.get(
        f"{BASE_URL}/check-newest-wisp",
        params={"wisp_id": "abcd" * 8}
    )
    assert response.status_code == 404

    NUM_TEST_WISPS = 10
    wisp_texts = [f"TEST WISP {i}" for i in range(NUM_TEST_WISPS)]
    for text in wisp_texts:
        response = user_sess.post(
            f"{BASE_URL}/post-wisp",
            json={"text": text}
        )
        assert response.status_code == 201

    response = user_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    assert response.status_code == 200
    wisps = response.json()["wisps"]
    assert (len(wisps) == appconfig["MAX_WISPS_PER_USER"] and
        wisps[0]["text"] == wisp_texts[-1])
    
    for i in range(NUM_TEST_WISPS):
        response = user_sess.get(
            f"{BASE_URL}/check-newest-wisp",
            params={"wisp_id": wisps[i]["wisp_id"]}
        )
        assert response.status_code == 200
        assert response.json()["newest"] == (i == 0)

def dummy_test_purge_old_wisps(user_sess, test_wisp):
    response = user_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    assert (response.status_code == 200 and
        len(response.json()["wisps"]) == 1)

    time.sleep(7)

    response = user_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    assert (response.status_code == 200 and
        len(response.json()["wisps"]) == 0)

def test_remembrances(user_sess, user_2_sess):
    for i in range(appconfig["MAX_WISPS_PER_USER"]):
        response = user_sess.post(
            f"{BASE_URL}/post-wisp",
            json={"text": str(i)}
        )
        assert response.status_code == 201

    for _ in range(appconfig["MAX_WISPS_PER_USER"]):
        response = user_2_sess.post(
            f"{BASE_URL}/post-wisp",
            json={"text": "filler"}
        )
        assert response.status_code == 201

    response = user_sess.get(
        f"{BASE_URL}/get-remembrances"
    )
    assert response.status_code == 200
    rems = response.json()["remembrances"]
    assert len(rems) == appconfig["MAX_REMEMBRANCES"]
    rems = sorted(rems, key=lambda rem: int(rem["text"]))
    print(rems)
    for i in range(appconfig["MAX_REMEMBRANCES"]):
        assert rems[i]["text"] == str(i)
    
    response = user_sess.get(
        f"{BASE_URL}/get-wisps"
    )
    wisp = response.json()["wisps"][-1]
    response = user_sess.post(
        f"{BASE_URL}/heart-wisp",
        json={"wisp_id": wisp["wisp_id"]}
    )
    assert response.status_code == 200
    
    response = user_sess.post(
        f"{BASE_URL}/post-wisp",
        json={"text": "filler"}
    )
    assert response.status_code == 201
    response = user_sess.get(
        f"{BASE_URL}/get-remembrances"
    )
    assert response.status_code == 200
    rems = response.json()["remembrances"]
    assert len(rems) == appconfig["MAX_REMEMBRANCES"]
    print(rems)
    
