"""
Server initialization actions.
"""
import os
import time
from flask.wrappers import Response
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
import logging

from app import flaskapp, radiocontroller
from app import scheduled_tasks

def startup():
    """
    Startup configuration, logging, and task scheduling function
    """
    logging.basicConfig(
        filename=flaskapp.config["LOGFILE"],
        format=("%(asctime)s - %(name)s - %(levelname)s -" +
            "%(funcName)s():%(lineno)d - %(message)s"),
        level=flaskapp.config["LOGLEVEL"],
        datefmt="%Y-%m-%d %H:%M:%S") 
    file_handler = logging.FileHandler(flaskapp.config["LOGFILE"])
    flaskapp.logger.addHandler(file_handler)

    scheduled_tasks.schedule()

    radiocontroller.startup()
