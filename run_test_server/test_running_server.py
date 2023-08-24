import pytest
import time
from datetime import datetime as dt
from run_test_server import constants as testconstants

def test_full_server(user_sess, user_2_sess):
    while True:
        resp = user_sess.post(
            f"{testconstants.BASE_URL}/post-wisp",
            data={
                "text": f"The time is now {dt.now().isoformat()}",
                "gif_uri": "80fcef798f5d19985fad8927dc3b6daf" +
                           "0534c09d4125e89689590865a8c407d3"
            }
        )
        time.sleep(5)
        resp = user_2_sess.post(
            f"{testconstants.BASE_URL}/post-wisp",
            data={"text": f"The time is now {dt.now().isoformat()}"}
        )
        time.sleep(5)
