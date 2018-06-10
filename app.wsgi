import sys
import os

OGGM_DASH_DIR = os.path.dirname(os.path.realpath(__file__))
os.chdir(OGGM_DASH_DIR)
sys.path.insert(0, OGGM_DASH_DIR)

from app import application
