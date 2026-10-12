import os
import sys

# Ensure the project root directory is on the Python module search path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import the initialized Flask instance
from app import app
