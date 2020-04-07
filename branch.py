import os
import os.path
import pathlib
import sys
from shutil import copyfile

from constants import *


def branch(name):
    head_file = os.path.join(MAIN_DIR_NAME, HEAD_FILE)
    with open(head_file, 'r') as f:
        head_file_content = f.read()
        _, ref = head_file_content.split().strip()
    ref_new_branch = os.path.join(MAIN_DIR_NAME, REFS_DIR, name)
    copyfile(ref, ref_new_branch)
