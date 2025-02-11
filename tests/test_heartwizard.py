"""
Test suite for HeartWizard actions.
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

def test_check_heartwizard(test_wisp, user_sess, user_2_sess):
    response = user_sess.get(
        f"{BASE_URL}/check-heartwizard"
    )
    assert response.status_code == 200 and response.json()["heartwizard"]
    
    response = user_2_sess.get(
        f"{BASE_URL}/check-heartwizard"
    )
    assert response.status_code == 200 and response.json()["heartwizard"]
   
    response = user_2_sess.post(
        f"{BASE_URL}/heart-wisp",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200

    response = user_sess.get(
        f"{BASE_URL}/check-heartwizard"
    )
    assert response.status_code == 200 and response.json()["heartwizard"]
    
    response = user_2_sess.get(
        f"{BASE_URL}/check-heartwizard"
    )
    assert (response.status_code == 200 and 
        not response.json()["heartwizard"])
   
    time.sleep(appconfig["WISP_LIFESPAN"].seconds * 1.5)
    response = user_sess.get(
        f"{BASE_URL}/check-heartwizard"
    )
    assert response.status_code == 200 and response.json()["heartwizard"]

    response = user_2_sess.get(
        f"{BASE_URL}/check-heartwizard"
    )
    assert response.status_code == 200 and response.json()["heartwizard"]

def test_get_ui(req_sess):
    response = req_sess.get(
        f"{BASE_URL}/get-ui"
    )
    assert (response.status_code == 200 and 
        response.json() == appconfig["DEFAULT_UICONFIG"])

def test_set_ui(user_sess, user_2_sess, test_wisp):
    response = user_2_sess.post(
        f"{BASE_URL}/heart-wisp",
        json={"wisp_id": test_wisp["wisp_id"]}
    )
    assert response.status_code == 200

    test_ui = {
        "font": appconfig["FONTS"][-1],
        "device": appconfig["DEVICES"][-1],
        "color_palette": appconfig["COLOR_PALETTES"][-1]
    }

    response = user_sess.post(
        f"{BASE_URL}/set-ui",
        json=test_ui
    )
    assert response.status_code == 200

    response = user_sess.get(
        f"{BASE_URL}/get-ui"
    )
    assert (response.status_code == 200 and 
        response.json() == test_ui)

    response = user_2_sess.get(
        f"{BASE_URL}/get-ui"
    )
    assert (response.status_code == 200 and 
        response.json() == test_ui)

    response = user_2_sess.post(
        f"{BASE_URL}/set-ui",
        json=appconfig["DEFAULT_UICONFIG"]
    )
    assert response.status_code == 403

    response = user_sess.get(
        f"{BASE_URL}/get-ui"
    )
    assert (response.status_code == 200 and 
        response.json() == test_ui)

