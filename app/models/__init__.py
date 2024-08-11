"""
Initialzation for "models" module. Allows for easy import of all
    module objects using "from app.models import *"
"""
import os

moddir = os.path.dirname(os.path.abspath(__file__))
for _, _, files in os.walk(moddir):
    for file in files:
        if file.endswith(".py"):
            exec(f"from .{file[:-3]} import *")
