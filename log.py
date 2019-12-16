import os
import os.path as pt
import zipfile
import hashlib
from shutil import copyfile
import time


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
LOG_FILE = 'log'

def log(files = None):
    #TODO: список измененных файлов между двумя коммитами
    log_file = pt.join(CVS_DIR_NAME, LOG_FILE)
    with open(log_file, 'r') as log:
        print(log.read())



def add_log(commit_hash):
    """Получает полный хэш коммита, с папкой"""
    log_file = pt.join(CVS_DIR_NAME, LOG_FILE)
    commit_path = pt.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME,commit_hash[0:2], commit_hash[2:])
    commit_create_time =time.ctime(pt.getctime(commit_path)) 
    with open(log_file, 'a') as log:
        print(f'commit: {commit_hash}',file=log)
        print(f'Data: {commit_create_time}\n',file=log)