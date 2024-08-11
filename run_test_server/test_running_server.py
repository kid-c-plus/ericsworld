import pytest
import time
from datetime import datetime as dt
from run_test_server import constants as testconstants

def test_full_server(user_sess, user_2_sess):
    while True:
        for i in range(10):
            resp = user_sess.post(
                f"{testconstants.BASE_URL}/post-wisp",
                json={
                    "text": f"The time is now {dt.now().isoformat()}",
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
                json={"text": f"The time is now {dt.now().isoformat()}"},
                verify=False
            )
            print(resp.text)
            assert resp.status_code == 201
            time.sleep(5)
        token = user_sess.get(f"{testconstants.BASE_URL}/hai").json()["csrftoken"]
        user_sess.headers["X-CSRFToken"] = token
        token_2 = user_2_sess.get(f"{testconstants.BASE_URL}/hai").json()["csrftoken"]
        user_2_sess.headers["X-CSRFToken"] = token_2
