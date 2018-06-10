#!/usr/bin/env python3

import sys
import os
from app import application

OGGM_DASH_DIR = os.path.dirname(os.path.realpath(__file__))
os.chdir(OGGM_DASH_DIR)
sys.path.insert(0, OGGM_DASH_DIR)

if __name__ == '__main__':
    application.run(debug=True, threaded=True)
