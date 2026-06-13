import sys
import os

# Add src folder to the path so pytest can resolve imports inside src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
