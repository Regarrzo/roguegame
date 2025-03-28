
import sys

MIN_VER = (3, 13)

if sys.version_info[:2] < MIN_VER:
    print("This game might or might not work with your version of Python. It was created with 3.13.")

import src.main