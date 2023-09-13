"""
Server deinitialization actions.
"""

from app import scheduled_tasks, radiocontroller

def shutdown():
    """
    Shutdown function, clears scheduled tasks.
    """
    scheduled_tasks.stop()
    radiocontroller.shutdown()
