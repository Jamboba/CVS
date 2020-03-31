import os
import os.path
import sys
from shutil import copyfile

from checkout import update_catalog_and_index, diff

CVS_DIR_NAME = '.aw'
CVS_DIR_OBJ_NAME = 'objects'
CVS_REPOS_INDEX = 'index'
ROOT_DIR = '.'
REFS_DIR = 'refs'
HEAD_FILE = 'head'


def reset(branch):
    """Текущая ветка указывает на тот же коммит, что и branch
        обновление содержимого каталога, индекса"""

    head_file = os.path.join(CVS_DIR_NAME, HEAD_FILE)
    with open(head_file, 'r') as f:
        current_branch_path = f.read().split(' ')[1].strip()
    reset_branch_path = os.path.join(CVS_DIR_NAME, REFS_DIR, branch)
    copyfile(reset_branch_path, current_branch_path)
    with open(reset_branch_path, 'r') as f:
        commit_name = f.read().strip()
    update_catalog_and_index(commit_name)
    index_path = os.path.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    diff(commit_name, index_path)
