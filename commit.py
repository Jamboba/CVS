import os
import os.path
from shutil import copyfile

from atomic import get_hash_for_path
from log import add_log

CVS_DIR_NAME = '.aw'
CVS_REPOS_INFO = 'info.txt'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
TXT_EXTENSION = '.txt'
ROOT_DIR = '.'
HEAD_FILE = 'head'


def commit(tag=None):
    index_path = os.path.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    commit_hash = get_hash_for_path(index_path)
    commit_dir_path = os.path.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME, commit_hash[0:2])
    try:
        os.mkdir(commit_dir_path)
    except FileExistsError as e:
        print(e)
        return
    commit_file_path = os.path.join(commit_dir_path, commit_hash[2:])
    copyfile(index_path, commit_file_path)
    write_ref(commit_hash)
    add_log(commit_hash)


def write_ref(hash):
    head_file = os.path.join(CVS_DIR_NAME, HEAD_FILE)
    with open(head_file, 'r') as head:
        ref = head.read().split(' ')[1].strip()
    with open(ref, 'w') as rf:
        print(hash, file=rf)
