import sys
import os
try:
    assert sys.version_info >= (3, 10)
except:
    print("WARNING: Update python compiler to >3.10\n")
os.system('py -m pip install --upgrade pip')
os.system('py -m pip install --upgrade Pillow')
os.system('py -m pip install --upgrade customtkinter')
os.system('py -m pip install --upgrade opencv-python')
