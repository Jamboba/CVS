import os
import os.path as pt
import pathlib
import sys
from shutil import copyfile

CVS_DIR_NAME = '.aw'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
HEAD_FILE = 'head'
LOG_FILE = 'log'
TAG_FILE = 'tag'
REFS_DIR = 'refs'
ROOT_DIR = '.'


def branch(name):
    head_file = pt.join(CVS_DIR_NAME, HEAD_FILE)
    with open(head_file, 'r') as f:
        ref = f.read().split(' ')[1].strip()
    ref_new_branch = pt.join(CVS_DIR_NAME, REFS_DIR, name)
    copyfile(ref, ref_new_branch)
