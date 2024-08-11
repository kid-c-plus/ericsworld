"""
Flask after-request function to add CSRF token.
"""
from flask.wrappers import Response
from flask_wtf.csrf import generate_csrf

from app import flaskapp

@flaskapp.route("/hai", methods=["GET"])
def hai():
    """
    Stub method for recieving CSRF token.
    :return: {"csrftoken"} 200 response
    """
    return {"csrftoken": generate_csrf()}, 200

"""
@flaskapp.after_request
def add_csrf_cookie(response: Response):
    ""
    Called after Flask response is generated. If response is
        successful, add the X-CSRF-Token.
    :param response: Flask Response object to add token to
    :return: response, with token if successful
    ""
    if (response.status_code in range(200, 400) and
            not response.direct_passthrough):
        response.set_cookie(
            "csrftoken", generate_csrf(), secure=True
        )
    return response
"""
