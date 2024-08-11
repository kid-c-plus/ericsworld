"""
App defining global constant values.
"""
from werkzeug.security import generate_password_hash

# User status integers
INVITED_USER = 1
ACTIVE_USER = 2
DISABLED_USER = 3

# Wisp status integers
LIVE_WISP = 1
REMEMBRANCE_WISP = 2

# Song status integers
QUEUED_SONG = 1
PLAYING_SONG = 2
PLAYED_SONG = 3

# Test code used when Twilio support is disabled
TEST_AUTH_CODE = "123456"

# Dummy hash used to pad out response time for not-found users
DUMMY_HASH = generate_password_hash("DUMMY_STRING")

# Local file to store reset token for unit testing
RESET_TOKEN_FILE = "reset_token.txt"
