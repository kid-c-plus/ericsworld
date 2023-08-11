"""
Fixtures shared between multiple test suites.
"""
import pytest
import os
import requests

from sqlalchemy.orm import sessionmaker

from test_config import Config
from tests import constants as testconstants

# delete all previous content from testing Logfile
if os.path.exists(Config.LOGFILE):
     f = open(Config.LOGFILE, "w")
     f.seek(0)
     f.truncate()

from app import *

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
    start_server()

    # Resource (none needed)
    yield None

    # Teardown
    stop_server()

@pytest.fixture
def db_resource():
    """
    Set up Flask db context and create db fixture.
    """
    # Setup
    flaskapp.app_context().push()
    # Just verify that this is the test database
    assert (db.engine.url.database.split(os.path.sep)[-1] == 
        "test_app.db"
    )
    db.metadata.create_all(db.engine)

    # Resource
    yield db

    # Teardown
    db.session.remove()
    db.drop_all()

@pytest.fixture
def req_sess():
    """
    Set up Requests session with CSRF Token.
    """
    # Setup
    s = requests.Session()
    s.get(f"{testconstants.BASE_URL}/hai")
    s.headers["X-CSRFToken"] = s.cookies["csrftoken"]

    # Resource
    yield s

    # Teardown
    s.close()

@pytest.fixture
def test_user(db_resource):
    """
    Set up active test user.
    """
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
def user_sess(test_user, req_sess):
    # Set up
    
    response = req_sess.post(f"{testconstants.BASE_URL}/login", data={
        "phone_number": test_user.phone_number,
        "password": testconstants.TEST_PASSWORD
    })
    assert response.status_code == 200
    
    # Resource
    yield req_sess

    # No teardown

@pytest.fixture
def test_user_2(db_resource):
    """
    Set up second active test user.
    """
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
def user_2_sess(test_user_2, req_sess):
    # Set up
    response = req_sess.post(f"{testconstants.BASE_URL}/login", data={
        "phone_number": test_user_2.phone_number,
        "password": testconstants.TEST_PASSWORD
    })
    assert response.status_code == 200
    
    # Resource
    yield req_sess

    # No teardown

