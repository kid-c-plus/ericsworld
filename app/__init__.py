"""
Server app initialization stub.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import sys
from twilio.rest import Client
from multiprocessing import Process

flaskapp = Flask(__name__)
# Load basic config if production,
# or test config if testing (i.e. if "pytest" is loaded)
if "pytest" in sys.modules:
    from test_config import Config
else:
    from config import Config
flaskapp.config.from_object(Config)
appconfig = flaskapp.config

CSRFProtect(flaskapp)
CORS(flaskapp)

db = SQLAlchemy(flaskapp)
migrate = Migrate(flaskapp, db, render_as_batch=True)

# Twilio is disabled for pytest
if appconfig["USE_TWILIO"]:
    twilio_client = Client(
        appconfig["TWILIO_ACCOUNT_SID"],
        appconfig["TWILIO_AUTH_TOKEN"]
    )
else:
    twilio_client = None

loginmanager = LoginManager()
loginmanager.init_app(flaskapp)
loginmanager.unauthorized_handler(
    lambda : ({"error": "No authenticated user."}, 401)
)

from app.models import *
from app.views import *

from app.radio_controller import RadioController
radiocontroller = RadioController()

# Create and start task scheduler
scheduler = BackgroundScheduler()
from app import startup, shutdown
startup.startup()
atexit.register(shutdown.shutdown)

# Convenience methods for Pytest
# if "pytest" in sys.modules:

def start_server() -> Process:
    """
    Start function, invoked only in testing. Starts task in separate
        thread.
    :return: Server process thread
    """
    server = Process(target=lambda : flaskapp.run(
        **appconfig["FLASK_RUN_ARGS"]
    ))
    try:
        server.start()
    except NameError:
        print("Must be invoked with pytest")
    return server

def stop_server(server_thread: Process):
    """
    Stop function, invoked only in testing. Stops task thread.
    :param server_thread: Server process thread to stop
    """
    shutdown.shutdown()
    try:
        server_thread.terminate()
        server_thread.join()
    except NameError:
        print("Must be invoked with pytest")

