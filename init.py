import os
import os.path
import sys

from constants import *


def init(is_cvs=True):
    """ Создает папку .aw в директории, с которой будем работать
        is_cvs - если иницализируем CVS"""

    os.mkdir(MAIN_DIR_NAME)
    object_dir = os.path.join(MAIN_DIR_NAME, OBJ_DIR_NAME)
    os.mkdir(object_dir)
    refs_dir = os.path.join(MAIN_DIR_NAME, REFS_DIR)
    os.mkdir(refs_dir)
    master_ref = os.path.join(MAIN_DIR_NAME, REFS_DIR, MASTER_REF_FILE)
    head_file = os.path.join(MAIN_DIR_NAME, HEAD_FILE)
    index_file = os.path.join(MAIN_DIR_NAME, REPOS_INDEX)
    tag_file = os.path.join(MAIN_DIR_NAME, TAG_FILE)
    open(index_file, 'a').close()
    with open(head_file, 'w') as headf:
        # print(f'ref: {master_ref}', file=headf)
        headf.write(f'ref: {master_ref}')
    open(tag_file, 'a').close()
    open(master_ref, 'a').close()
    if is_cvs:
        log_file = os.path.join(MAIN_DIR_NAME, LOG_FILE)
        open(log_file, 'a').close()
    print('initiated')
