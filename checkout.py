import os
import os.path as pt
import zipfile
import hashlib

import add
from commit import write_head

CVS_DIR_NAME = '.aw'
CVS_REPOS_INFO = 'info.txt'
CVS_REPOS_INDEX = 'index.txt'
CVS_DIR_OBJ_NAME = 'objects'
CVS_BLOB_OBJ = 'blob'
CVS_TREE_OBJ = 'tree'
CVS_DIR_TEMP = 'tmp'
TXT_EXTENSION = '.txt'
ROOT_DIR = '.'
COMMITS_DIR = 'commits'
ZIP_EXTENSION = '.zip'

def checkout(commit_name):
    #TODO: Проверка, хэш или имя
    commit_file_path = pt.join(CVS_DIR_NAME,CVS_DIR_OBJ_NAME,commit_name[0:2],commit_name[2:])
    with open(commit_file_path, 'r') as commit:
        while True:
            file_info = commit.readline()
            if(not file_info):
                break
            file_info = file_info.split(' ')
            filename = pt.split(file_info[0])
            zip_path = pt.join(CVS_DIR_NAME,CVS_DIR_OBJ_NAME, file_info[1][:2],file_info[1][2:-1]+ZIP_EXTENSION)
            target_path = pt.join(ROOT_DIR, filename[0])
            with zipfile.ZipFile(zip_path, mode = 'r') as zp:
                zp.extract(filename[1], target_path)
    write_head(commit_name)