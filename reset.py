import os
import os.path
import sys
from shutil import copyfile

from atomic import update_catalog_and_index, diff
from constants import *


def reset(branch):
    """Текущая ветка указывает на тот же коммит, что и branch
        обновление содержимого каталога, индекса"""

    # head_file = os.path.join(MAIN_DIR_NAME, HEAD_FILE)
    with open(head_file, 'r') as f:
        current_branch_path = f.read().split(' ')[1].strip()
    reset_branch_path = os.path.join(MAIN_DIR_NAME, REFS_DIR, branch)
    copyfile(reset_branch_path, current_branch_path)
    with open(reset_branch_path, 'r') as f:
        commit_name = f.read().strip()
    update_catalog_and_index(commit_name)
    # index_file = os.path.join(MAIN_DIR_NAME, REPOS_INDEX)
    diff(commit_name, index_file)
