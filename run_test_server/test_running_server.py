import pytest
import time
from datetime import datetime as dt
from run_test_server import constants as testconstants

def test_full_server(user_sess, user_2_sess, user_3_sess):
    for _ in range(5):
        for i in range(10):
            resp = user_sess.post(
                f"{testconstants.BASE_URL}/post-wisp",
                json={
                    "text": f"I love my computer",
                    "gif_uri": "80fcef798f5d19985fad8927dc3b6daf" +
                               "0534c09d4125e89689590865a8c407d3"
                },
                verify=False
            )
            print(resp.text)
            assert resp.status_code == 201
            time.sleep(5)
            resp = user_2_sess.post(
                f"{testconstants.BASE_URL}/post-wisp",
                json={"text": "please friend me on PSP"},
                verify=False
            )
            print(resp.text)
            assert resp.status_code == 201
            time.sleep(5)
            resp = user_3_sess.post(
                f"{testconstants.BASE_URL}/post-wisp",
                json={"text": "i love to smile with my buddys"},
                verify=False
            )
            print(resp.text)
            assert resp.status_code == 201
            time.sleep(300)
        token = user_sess.get(f"{testconstants.BASE_URL}/hai").json()["csrftoken"]
        assert token
        user_sess.headers["X-CSRFToken"] = token
        token_2 = user_2_sess.get(f"{testconstants.BASE_URL}/hai").json()["csrftoken"]
        assert token_2
        user_2_sess.headers["X-CSRFToken"] = token_2
    while True:
        time.sleep(10)
