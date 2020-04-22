import os.path
import pathlib
import sys
from shutil import copyfile

from constants import *


def branch(name):
    with open(head_file, 'r') as f:
        head_file_content = f.read()
        _, ref = head_file_content.split()
    ref_new_branch = os.path.join(MAIN_DIR_NAME, REFS_DIR, name)
    copyfile(ref, ref_new_branch)
