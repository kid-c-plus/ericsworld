"""
Test config file for invoking the server for frontend testing, as 
    defined in run_test_server/
"""
from datetime import timedelta
import logging
import os
import re

class Config:
    """
    Class containing all configuration items.
    """
    FLASK_RUN_ARGS = {
        "host": "0.0.0.0", 
        "ssl_context": "adhoc"
    }

    # SQLAlchemy Settings
    basedir = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "test_app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-WTF Settings
    # CSRF Protection enabled
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SSL_STRICT = False

    # Flask-CORS Settings
    CORS_ORIGINS = "http://localhost:3000"
    CORS_SUPPORTS_CREDENTIALS = True

    SECRET_KEY = "UNIMPORTANT_TEST_KEY"

    # Twilio Auth Settings
    USE_TWILIO = False

    # Logging Settings

    LOGFILE = os.path.join(basedir, "run_test_error.log")
    LOGLEVEL = logging.DEBUG

    # App Behavior Settings

    PROFILE_PATH = os.path.join(basedir, "app", "static", "profiles")
    GIF_PATH = os.path.join(basedir, "app", "static", "gifs")

    # Duration for which a password reset token is valid
    RESET_TOKEN_LIFESPAN = timedelta(seconds=5)
    # Timeout between initiating password resets
    RESET_PROCESS_TIMEOUT = timedelta(hours=24)
 
    # Interval for scheduled task to purge old Wisps, in seconds
    WISP_PURGE_INTERVAL = 1
    
    MAX_WISP_LENGTH = 140
    WISP_LIFESPAN = timedelta(seconds=60)
    MAX_WISPS = 300
    MAX_WISPS_PER_USER = 100
    MAX_REMEMBRANCES = 50
    
    # Number of Wisps to load per API request
    WISPS_PER_PAGE = 100
    
    # Maximum number of GIFs to return for a search
    # GIF search isn't paginated, for nonscalability
    GIFS_PER_SEARCH = 30

    MAX_INVITES = 50
    INVITE_MSG = ("You Have Been Invited To Join Eric's World! " +
        "A New And Unimagined Galaxy Awaits You Here: " +
        "http://ericsworld.net.")

    # number of people who must block an account before it's 
    # permabanned
    BLOCKS_TO_BAN = 2
    
    WEBMASTER_EMAIL = None

    # Phone number format validity check
    PHONE_NUMBER_CHECK = lambda number: (
        type(number) is str and 
        re.fullmatch(r"\+\d{11,13}", number) is not None
    )

    def EMAIL_CHECK(email: str) -> bool:
        """
        Email address check. Verifies length and regex match.
        :param email: email address to check
        :return: True if valid
        """
        EMAIL_MAX_LENGTH = 320
        EMAIL_REGEX = (
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        )
        return (type(email) is str and len(email) < EMAIL_MAX_LENGTH 
            and re.fullmatch(EMAIL_REGEX, email))

    def USERNAME_CHECK(username: str) -> bool:
        """
        Username length check. Does not check for uniqueness.
        :param username: username to check
        :return: True if valid
        """
        USERNAME_LENGTH_RANGE = (3, 12)
        return (type(username) is str and 
            len(username) >= USERNAME_LENGTH_RANGE[0] and 
            len(username) <= USERNAME_LENGTH_RANGE[1])

    def PASSWORD_CHECK(password: str) -> bool:
        """
        Password complexity check. Verifies length (as defined below),
            and character content
        :param password: password to check
        :return: True if valid
        """
        PASSWORD_LENGTH_RANGE = (10, 30)
        return (type(password) is str and 
            len(password) >= PASSWORD_LENGTH_RANGE[0] and
            len(password) <= PASSWORD_LENGTH_RANGE[1] and
            # ensure password contains only printable ASCII
            re.fullmatch(r"[ -~]*", password))

    def PROFILE_URI_CHECK(profile_uri: str) -> bool:
        """
        Profile URI check. Ensures that profile refers to an existing 
            profile picture. Profile URI should be sanitized before 
            checking
        :param profile_uri: URI to check
        :return: True if valid
        """
        return profile_uri and os.path.exists(os.path.join(
            Config.PROFILE_PATH, profile_uri
        ))

    def WISP_TEXT_CHECK(wisp_text: str) -> bool:
        """
        Wisp text check. Ensures that Wisp text exists and is below
            maximum length. Wisp text should be bleached before
            checking
        :param wisp_text: text of Wisp to check
        :return: True if valid
        """
        return wisp_text and len(wisp_text) < Config.MAX_WISP_LENGTH

    def GIF_URI_CHECK(gif_uri: str) -> bool:
        """
        GIF URI check. Ensures that provided GIF URI exists.
            GIF URI should be sanitized before checking
        :param gif_uri: GIF URI to check
        :return: True if valid
        """
        return gif_uri and os.path.exists(os.path.join(
            Config.GIF_PATH, gif_uri
        ))
