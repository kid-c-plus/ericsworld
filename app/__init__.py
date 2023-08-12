"""
Server app initialization stub.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import sys
from twilio.rest import Client

flaskapp = Flask(__name__)
# Load basic config if production,
# or test config if testing (i.e. if "pytest" is loaded)
if "pytest" in sys.modules:
    from test_config import Config
else:
    from config import Config
flaskapp.config.from_object(Config)
appconfig = flaskapp.config

db = SQLAlchemy(flaskapp)
migrate = Migrate(flaskapp, db, render_as_batch=True)

# Twilio is disabled for pytest
if flaskapp.config["USE_TWILIO"]:
    twilio_client = Client(
        flaskapp.config["TWILIO_ACCOUNT_SID"],
        flaskapp.config["TWILIO_AUTH_TOKEN"]
    )
else:
    twilio_client = None

loginmanager = LoginManager()
loginmanager.init_app(flaskapp)
loginmanager.login_view = "login"

# Create and start task scheduler
scheduler = BackgroundScheduler()
from app import startup, shutdown
startup.startup()
atexit.register(shutdown.shutdown)

from app.models import *
from app.views import *

# Convenience methods for Pytest
# if "pytest" in sys.modules:
from multiprocessing import Process
server = Process(target=flaskapp.run)

def start_server():
    """
    Start function, invoked only in testing. Starts task in separate
        thread.
    """
    try:
        server.start()
    except NameError:
        print("Must be invoked with pytest")

def stop_server():
    """
    Stop function, invoked only in testing. Stops task thread.
    """
    try:
        server.terminate()
        server.join()
    except NameError:
        print("Must be invoked with pytest")
