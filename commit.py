import os
import os.path as pt
import zipfile
import hashlib
from shutil import copyfile

import add
from log import add_log

CVS_DIR_NAME = '.aw'
CVS_REPOS_INFO = 'info.txt'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
CVS_BLOB_OBJ = 'blob'
CVS_TREE_OBJ = 'tree'
CVS_DIR_TEMP = 'tmp'
TXT_EXTENSION = '.txt'
ROOT_DIR = '.'
HEAD_FILE = 'head'



def commit(tag = None):


    index_path = pt.join(CVS_DIR_NAME,CVS_REPOS_INDEX)
    commit_hash = add.hash_obj(index_path)
    commit_dir_path = pt.join(CVS_DIR_NAME,CVS_DIR_OBJ_NAME,commit_hash[0:2])
    try:
        os.mkdir(commit_dir_path)
    except FileExistsError as e:
        print(e)
        return
    commit_file_path = pt.join(commit_dir_path,commit_hash[2:])
    copyfile(index_path, commit_file_path)
    write_ref(commit_hash)
    add_log(commit_hash)

def write_ref(hash):
    head_file = pt.join(CVS_DIR_NAME,HEAD_FILE)
    with open (head_file, 'r') as f:
        ref = f.read().split(' ')[1].strip()
        # print('!', ref)
    with open (ref, 'w') as head:
        print(hash,file=head)
