"""
Fixtures shared between multiple test suites.
"""
import shutil
shutil.copy("run_test_config.py", "test_config.py")

import signal

import pytest
import sys
import os
import requests

try:
    os.remove("test_app.db")
except Exception:
    pass

from sqlalchemy.orm import sessionmaker

from test_config import Config
from run_test_server import constants as testconstants

# delete all previous content from testing Logfile
if os.path.exists(Config.LOGFILE):
     f = open(Config.LOGFILE, "w")
     f.seek(0)
     f.truncate()

from app import *
from build_gif_table import *

@pytest.fixture(autouse=True)
def remove_reset_token():
    # delete previous reset token file
    try:
        os.remove(constants.RESET_TOKEN_FILE)
    except FileNotFoundError:
        pass

@pytest.fixture(autouse=True, scope="session")
def server():
    """
    Run module-level server instance for testing.
    """
    # Setup
    thread = start_server()
    
    # Resource (none needed)
    yield None

    # Teardown
    stop_server(thread)

@pytest.fixture
def db_resource():
    # Setup
    flaskapp.app_context().push()
    # Just verify that this is the test database
    assert (db.engine.url.database.split(os.path.sep)[-1] == 
        "test_app.db"
    )

    db.metadata.create_all(db.engine)
    
    with open("gif_manifest.json") as manifest_file:
        fetcher = ManifestFetcher(manifest_file)
        builder = DatabaseBuilder(fetcher, db)
        builder.build()
    
    # Resource
    yield db

    # Teardown
    db.session.remove()
    db.drop_all()

@pytest.fixture
def req_sess():
    # Setup
    s = requests.Session()
    token = s.get(f"{testconstants.BASE_URL}/hai", verify=False).json()["csrftoken"]
    s.headers["X-CSRFToken"] = token

    # Resource
    yield s

    # Teardown
    s.close()

@pytest.fixture
def test_user(db_resource):
    # Setup
    session = sessionmaker(
            bind=db_resource.engine,
            expire_on_commit=False)()
    user = User(**testconstants.TEST_USER)
    user.set_password(testconstants.TEST_PASSWORD)
    session.add(user)
    session.commit()
    
    # Resource
    yield user

    # No teardown

@pytest.fixture
def user_sess(test_user):
    # Setup
    s = requests.Session()
    token = s.get(f"{testconstants.BASE_URL}/hai", verify=False).json()["csrftoken"]
    s.headers["X-CSRFToken"] = token

    response = s.post(f"{testconstants.BASE_URL}/login", json={
        "phone_number": test_user.phone_number,
        "password": testconstants.TEST_PASSWORD
    }, verify=False)
    print(response.text)
    assert response.status_code == 200
    
    # Resource
    yield s

    # No teardown

@pytest.fixture
def test_wisp(user_sess):
    # Setup
    user_sess.post(
        f"{testconstants.BASE_URL}/post-wisp",
        data=testconstants.TEST_WISP,
        verify=False
    )
    response = user_sess.get(
        f"{testconstants.BASE_URL}/get-wisps",
        verify=False
    )
    assert response.status_code == 200
    wisps = response.json()["wisps"]

    # Resource
    yield wisps[0]

    # No teardown

@pytest.fixture
def test_user_2(db_resource):
    # Setup
    session = sessionmaker(
            bind=db_resource.engine,
            expire_on_commit=True)()
    user = User(**testconstants.TEST_USER_2)
    user.set_password(testconstants.TEST_PASSWORD)
    session.add(user)
    session.commit()
    
    # Resource
    yield user

    # No teardown

@pytest.fixture
def user_2_sess(test_user_2):
    # Setup
    s = requests.Session()
    token = s.get(f"{testconstants.BASE_URL}/hai", verify=False).json()["csrftoken"]
    s.headers["X-CSRFToken"] = token

    response = s.post(f"{testconstants.BASE_URL}/login", json={
        "phone_number": test_user_2.phone_number,
        "password": testconstants.TEST_PASSWORD
    }, verify=False)
    assert response.status_code == 200
    
    # Resource
    yield s

    # No teardown

@pytest.fixture
def test_wisp_2(user_2_sess):
    # Setup
    user_2_sess.post(
        f"{testconstants.BASE_URL}/post-wisp",
        data=testconstants.TEST_WISP,
        verify=False
    )
    response = user_2_sess.get(
        f"{testconstants.BASE_URL}/get-wisps",
        verify=False
    )
    assert response.status_code == 200
    wisps = response.json()["wisps"]

    # Resource
    yield wisps[0]

    # No teardown

@pytest.fixture
def test_user_3(db_resource):
    # Setup
    session = sessionmaker(
            bind=db_resource.engine,
            expire_on_commit=True)()
    user = User(**testconstants.TEST_USER_3)
    user.set_password(testconstants.TEST_PASSWORD)
    session.add(user)
    session.commit()
    
    # Resource
    yield user

    # No teardown

@pytest.fixture
def user_3_sess(test_user_3):
    # Setup
    s = requests.Session()
    token = s.get(f"{testconstants.BASE_URL}/hai", verify=False).json()["csrftoken"]
    s.headers["X-CSRFToken"] = token

    response = s.post(f"{testconstants.BASE_URL}/login", json={
        "phone_number": test_user_3.phone_number,
        "password": testconstants.TEST_PASSWORD
    }, verify=False)
    assert response.status_code == 200
    
    # Resource
    yield s

    # No teardown
