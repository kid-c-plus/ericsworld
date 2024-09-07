"""
Test suite for radio functionality.
"""
import os
import sys
import time

sys.path.append(os.getcwd())

import pytest

from app import constants as appconstants
from app import appconfig
from app.models import *

from tests.constants import *

SNIPPET_LENGTH = 5
SONG_1 = "snippet - tellur - WLKARND.mp3"
SONG_2 = "snippet - quillyear - nottingham acid.mp3"

def test_queue_song(user_sess):
    response = user_sess.post(
        f"{BASE_URL}/queue-song",
        json={'song_uri': SONG_1})
    assert response.status_code == 201
    time.sleep(SNIPPET_LENGTH)
    for _ in range(SNIPPET_LENGTH * 3):
        queuer = user_sess.get(
            f"{BASE_URL}/get-song-queuer")
        assert queuer.status_code == 200
        if queuer.json().get("queueing_user_id") == TEST_USER["user_id"]:
            return
        time.sleep(1)
    # user song not queued
    assert False

def test_queue_many_songs(user_sess, user_2_sess):
    response = user_sess.post(
        f"{BASE_URL}/queue-song",
        json={'song_uri': SONG_1})
    assert response.status_code == 201
    response = user_sess.post(
        f"{BASE_URL}/queue-song",
        json={'song_uri': SONG_2})
    assert response.status_code == 403
    response = user_2_sess.post(
        f"{BASE_URL}/queue-song",
        json={'song_uri': SONG_2})
    assert response.status_code == 201
    time.sleep(SNIPPET_LENGTH)
    for _ in range(SNIPPET_LENGTH * 3):
        queuer = user_sess.get(
            f"{BASE_URL}/get-song-queuer")
        assert queuer.status_code == 200
        if queuer.json().get("queueing_user_id") == TEST_USER["user_id"]:
            break
        time.sleep(1)
    else:
        # user song not queued
        assert False
    time.sleep(SNIPPET_LENGTH)
    for _ in range(SNIPPET_LENGTH * 3):
        queuer = user_sess.get(
            f"{BASE_URL}/get-song-queuer")
        assert queuer.status_code == 200
        if queuer.json().get("queueing_user_id") == TEST_USER_2["user_id"]:
            break
        time.sleep(1)
    else:
        # user song not queued
        assert False

def test_skip_song(user_sess, user_2_sess, user_3_sess):
    response = user_sess.post(
        f"{BASE_URL}/queue-song",
        json={'song_uri': SONG_1})
    assert response.status_code == 201
    for _ in range(SNIPPET_LENGTH * 3):
        queuer = user_sess.get(
            f"{BASE_URL}/get-song-queuer")
        assert queuer.status_code == 200
        if queuer.json().get("queueing_user_id") == TEST_USER["user_id"]:
            resp = user_3_sess.post(
                f"{BASE_URL}/brokenheart-song")
            assert resp.status_code == 200
            resp = user_2_sess.post(
                f"{BASE_URL}/brokenheart-song")
            assert resp.status_code == 200
            time.sleep(0.5)
            queuer = user_sess.get(
                f"{BASE_URL}/get-song-queuer")
            assert queuer.status_code == 200
            assert queuer.json().get(
                "queueing_user_id") != TEST_USER["user_id"]
            return
        time.sleep(1)
    # user song not queued
    assert False
