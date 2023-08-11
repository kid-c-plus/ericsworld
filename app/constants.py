"""
App defining global constant values.
"""
from werkzeug.security import generate_password_hash

# Account status integers
INVITED_ACCOUNT = 1
ACTIVE_ACCOUNT = 2
DISABLED_ACCOUNT = 3

# Wisp status integers
LIVE_WISP = 1
REMEMBRANCE_WISP = 2

# Test code used when Twilio support is disabled
TEST_AUTH_CODE = "123456"

# Dummy hash used to pad out response time for not-found users
DUMMY_HASH = generate_password_hash("DUMMY_STRING")

# Local file to store reset token for unit testing
RESET_TOKEN_FILE = "reset_token.txt"
