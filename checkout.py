import os
import os.path as pt
import zipfile
import hashlib

import add
from commit import write_ref

CVS_DIR_NAME = '.aw'
CVS_REPOS_INFO = 'info.txt'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
CVS_BLOB_OBJ = 'blob'
CVS_TREE_OBJ = 'tree'
CVS_DIR_TEMP = 'tmp'
TXT_EXTENSION = '.txt'
ROOT_DIR = '.'
COMMITS_DIR = 'commits'
ZIP_EXTENSION = '.zip'
TAG_FILE = 'tag'
REFS_DIR = 'refs'
HEAD_FILE = 'head'

def checkout(commit_name):
    check_tag = is_tag(commit_name)
    print(check_tag)
    if check_tag:
        commit_name = check_tag
    check_branch = is_branch(commit_name)
    if check_branch:
        print('Это ветка')
        write_head(commit_name)
        commit_name = check_branch
    #TODO: Проверка, хэш или тег или ветка
    commit_file_path = pt.join(CVS_DIR_NAME,CVS_DIR_OBJ_NAME,commit_name[0:2],commit_name[2:])
    with open(commit_file_path, 'r') as commit:
        while True:
            file_info = commit.readline()
            if not file_info:
                break
            file_info = file_info.split(' ')
            filename = pt.split(file_info[0])
            zip_path = pt.join(CVS_DIR_NAME,CVS_DIR_OBJ_NAME, file_info[1][:2],file_info[1][2:-1]+ZIP_EXTENSION)
            target_path = pt.join(ROOT_DIR, filename[0])
            with zipfile.ZipFile(zip_path, mode = 'r') as zp:
                zp.extract(filename[1], target_path)
    write_ref(commit_name)

def is_branch(commit_name):
    ref_file = pt.join(CVS_DIR_NAME,REFS_DIR,commit_name)
    if os.path.exists(ref_file):
        with open(ref_file, 'r') as f:
            commit_hash = f.read().strip()
        return commit_hash
    else:
        return

def is_tag(commit_name):
    tag_file = pt.join(CVS_DIR_NAME, TAG_FILE)
    with open(tag_file,'r') as tagf:
        tag_list = tagf.readlines()

        try:
            tagging_commit = list(filter(lambda x: x.split(' ')[0].find(commit_name)>-1,tag_list))[0]
            return tagging_commit.split(' ')[1]
        except IndexError as e:
            print(e)
            return

def write_head(name):
    head_file = pt.join(CVS_DIR_NAME,HEAD_FILE)
    name_ref = pt.join(CVS_DIR_NAME,REFS_DIR,name)
    with open (head_file, 'w') as f:
        print(f'ref: {name_ref}',file=f)

