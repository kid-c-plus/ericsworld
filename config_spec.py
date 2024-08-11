"""
Specification for configuration file - all application settings should be set here.
"""
from datetime import timedelta
import logging
import os
import re

class Config:
    """
    Class containing all configuration items.
    """
    FLASK_RUN_ARGS = {}

    # SQLAlchemy Settings
    basedir = os.path.abspath(os.path.dirname(__file__))


    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        basedir, "app.db")
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, "db_repository")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-WTF Settings
    # CSRF Protection enabled
    WTF_CSRF_ENABLED = True

    SECRET_KEY = "<RANDOMLY GENERATED SECRET KEY>"

    # Twilio Auth Settings
    USE_TWILIO = True
    TWILIO_ACCOUNT_SID = "<TWILIO ACCOUNT SID>"
    TWILIO_VERIFY_SERVICE_SID = "<TWILIO VERIFICATION SERVICE SID>"
    TWILIO_MSG_SERVICE_SID = "<TWILIO MESSAGING SERVICE SID>"
    TWILIO_AUTH_TOKEN = "<TWILIO AUTH TOKEN>"

    # Logging Settings

    LOGFILE = "<LOG FILE PATH>"
    LOGLEVEL = logging.DEBUG

    # Icecast Server Settings

    ICECAST_HOST = "127.0.0.1"
    ICECAST_PORT = 8000
    ICECAST_MOUNTPOINT = "stream"
    ICECAST_USERNAME = "source"
    ICECAST_PASSWORD = "<ICECAST PASSWORD>"
    ICECAST_FORMAT = "mp3"
    ICECAST_PROTOCOL = "http"
    ICECAST_NAME = "Radio Max"
    ICECAST_GENRE = "Dance"
    ICECAST_URL = "http://www.ericsworld.net"
    ICECAST_BITRATE = 128
    ICECAST_SAMPLERATE = 44100
    ICECAST_CHANNELS = 2

    # length of crossfade, in milliseconds
    CROSSFADE_LENGTH = 5000
    
    # App Behavior Settings

    PROFILE_PATH = os.path.join(basedir, "app", "static", "profiles")
    GIF_PATH = os.path.join(basedir, "app", "static", "gifs")
    SONG_PATH = os.path.join(basedir, "app", "static", "songs")
    ASSET_PATH = os.path.join(basedir, "app", "static", "assets")
    
    SKIP_MP3_PATH = os.path.join(ASSET_PATH, "skip.mp3")

    # Duration for which a password reset token is valid
    RESET_TOKEN_LIFESPAN = timedelta(hours=24)
    # Timeout between initiating password resets
    RESET_PROCESS_TIMEOUT = timedelta(hours=24)

    # Interval for scheduled task to purge old Wisps, in seconds
    WISP_PURGE_INTERVAL = 60
    
    MAX_WISP_LENGTH = 140
    WISP_LIFESPAN = timedelta(hours=24)
    MAX_WISPS = 5000
    MAX_WISPS_PER_USER = 100
    MAX_REMEMBRANCES = 50

    # Number of Wisps to load per API request
    WISPS_PER_PAGE = 100

    MAX_INVITES = 50
    INVITE_MSG = ("You Have Been Invited To Join Eric's World! " +
        "A New And Unimagined Galaxy Awaits You Here: " +
        "http://ericsworld.net.")

    # number of people who must block an account before it's 
    # permabanned
    BLOCKS_TO_BAN = 20

    WEBMASTER_EMAIL = "webmaster@ericsworld.net"

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

    def GIF_URI_CHECK(blingee_uri: str) -> bool:
        """
        GIF URI check. Ensures that provided GIF URI exists.
            GIF URI should be sanitized before checking
        :param gif_uri: GIF URI to check
        :return: True if valid
        """
        return gif_uri and os.path.exists(os.path.join(
            Config.GIF_PATH, gif_uri
        ))

    # UI Settings
    # lists of permitted fonts, device uris, and color palettes
    FONTS = ["jgs"]
    DEVICES = ["rubyred"]
    COLOR_PALETTES = ["valentine"]

    DEFAULT_UICONFIG = {
        "font": FONTS[0],
        "device": DEVICES[0],
        "color_palette": COLOR_PALETTES[0]
    }
