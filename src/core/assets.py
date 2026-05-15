import os
import sys
import logging

logger = logging.getLogger()

# Work out the base path for assets
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def load_asset(relative_path):
    """Load an asset from the given relative path."""
    full_path = os.path.join(base_path, relative_path)
    if not os.path.exists(full_path):
        logger.error(f"Asset not found: {full_path}")
        raise FileNotFoundError(f"Asset not found: {full_path}")
    return full_path
