"""
Functions for playing songs on Icecast stream, as well as contained
    management function to check song status, handle skips and 
    transitions, etc. Should be configured as a scheduled task in
    scheduled_tasks.py.
"""
import python-shout
from datetime import datetime

from app import flaskapp, db, appconfig
from app.models import Song

class RadioController():
    """
    Object encapsulating radio control functions - "manage" function
        should be scheduled to run about once per second.
    """
    def __init__(self): 
        """
        Initialization actions.
        """
        self.current_song = None
        
