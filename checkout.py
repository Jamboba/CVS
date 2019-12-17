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
    """ Принимает ветку, коммит, тег
        Перемещает HEAD на новую ветку"""
    check_tag = is_tag(commit_name)
    check_branch = is_branch(commit_name)
    print(check_tag)
    if check_tag:
        commit_name = check_tag
    if check_branch:
        write_head(commit_name)
        commit_name = check_branch
    else:
        write_ref(commit_name)
    update_catalog_and_index(commit_name)
    
    # write_ref(commit_name)

def is_branch(name):
    ref_file = pt.join(CVS_DIR_NAME,REFS_DIR,name)
    if os.path.exists(ref_file):
        with open(ref_file, 'r') as f:
            commit_hash = f.read().strip()
        return commit_hash
    else:
        return

def is_tag(name):
    tag_file = pt.join(CVS_DIR_NAME, TAG_FILE)
    with open(tag_file,'r') as tagf:
        tag_list = tagf.readlines()

        try:
            tagging_commit = list(filter(lambda x: x.split(' ')[0].find(name)>-1,tag_list))[0]
            return tagging_commit.split(' ')[1].strip()
        except IndexError as e:
            print(e)
            return

def write_head(name):
    head_file = pt.join(CVS_DIR_NAME,HEAD_FILE)
    name_ref = pt.join(CVS_DIR_NAME,REFS_DIR,name)
    with open (head_file, 'w') as f:
        print(f'ref: {name_ref}',file=f)

def update_catalog_and_index(commit_name):
    commit_file_path = pt.join(CVS_DIR_NAME,CVS_DIR_OBJ_NAME,commit_name[0:2],commit_name[2:])
    with open(commit_file_path, 'r') as commit:
        update_index = []
        while True:
            file_info = commit.readline()
            if not file_info:
                break
            update_index.append(file_info)
            file_info = file_info.split(' ')
            filename = pt.split(file_info[0])
            zip_path = pt.join(CVS_DIR_NAME,CVS_DIR_OBJ_NAME, file_info[1][:2],file_info[1][2:-1]+ZIP_EXTENSION)
            target_path = pt.join(ROOT_DIR, filename[0])
            with zipfile.ZipFile(zip_path, mode = 'r') as zp:
                zp.extract(filename[1], target_path)
    index_path = pt.join(CVS_DIR_NAME,CVS_REPOS_INDEX)
    diff(commit_file_path,index_path)
    with open(index_path, 'w') as index:
        for i in update_index:
            print(i,file=index)

def diff(new_index, old_index):
    with open(new_index) as new:
        files_new = {i.split(' ')[0] for i in new.readlines()}

    with open(old_index) as old:
        files_old = {i.split(' ')[0] for i in old.readlines()}
    
    if files_new.issubset(files_old):
        delete_files(files_old-files_new)

def delete_files(files):
    print(files)
    for file in files:
        os.remove(file)

