"""
Constants for testing.
"""
import uuid

from app import constants as appconstants

BASE_URL = "http://127.0.0.1:5000"
TEST_NEW_USER = {
    "user_id": uuid.uuid1().hex,
    "login_id": uuid.uuid1().hex,
    "phone_number": "+15555551234",
    "recovery_email": "testuser@ericsworld.net",
}

TEST_NEW_USER_2 = {
    "user_id": uuid.uuid1().hex,
    "login_id": uuid.uuid1().hex,
    "phone_number": "+15555555678",
    "recovery_email": "testuser@ericsworld.net",
}

TEST_USER = {
    "user_id": uuid.uuid1().hex,
    "login_id": uuid.uuid1().hex,
    "phone_number": "+15555550910",
    "recovery_email": "testuser@ericsworld.net",
    "username": "test user",
    "account_status": appconstants.ACTIVE_ACCOUNT,
    "profile_uri": "default"
}

TEST_USER_2 = {
    "user_id": uuid.uuid1().hex,
    "login_id": uuid.uuid1().hex,
    "phone_number": "+15555551112",
    "recovery_email": "testuser2@ericsworld.net",
    "username": "test user 2",
    "account_status": appconstants.ACTIVE_ACCOUNT,
    "profile_uri": "default"
}

TEST_USER_3 = {
    "user_id": uuid.uuid1().hex,
    "login_id": uuid.uuid1().hex,
    "phone_number": "+15555551314",
    "recovery_email": "testuser3@ericsworld.net",
    "username": "test user 3",
    "account_status": appconstants.ACTIVE_ACCOUNT,
    "profile_uri": "default"
}


TEST_PASSWORD = "Pa$$word1234"
TEST_PASSWORD_2 = "password5678"
TEST_PASSWORD_3 = "passW0RD9101"

TEST_WISP = {
    "text": "haiii :3",
    "gif_uri": "01309eb8d523ea5ac65fc888400e631a" + 
               "546fbd2af53e1f233f86be864d622fc4"
}
