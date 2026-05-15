import sys
import os

# Add the src directory to the path so we can import it
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.main import main

if __name__ == "__main__":
    main()
