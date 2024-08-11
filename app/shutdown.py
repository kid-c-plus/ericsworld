"""
Server deinitialization actions.
"""

from app import scheduled_tasks, radiocontroller

FILE = "thread_debug.txt"
with open(FILE, "w") as f:
    f.write("Starting server...")

def shutdown():
    """
    Shutdown function, clears scheduled tasks.
    """
    with open(FILE, "a") as f:
        f.write("Shutting down server in \"shutdown.shutdown\"")
    scheduled_tasks.stop()
    radiocontroller.shutdown()
