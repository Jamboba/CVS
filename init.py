import os
# import os.path
# import sys

from .constants import *


def init(is_cvs=True, script_dir=False):
    """ Создает папку .aw в директории, с которой будем работать
        is_cvs - если иницализируем CVS"""
    if script_dir:
        MAIN_DIR_NAME = script_dir
    print(MAIN_DIR_NAME)
    os.mkdir(MAIN_DIR_NAME)
    object_dir = os.path.join(MAIN_DIR_NAME, OBJ_DIR_NAME)
    os.mkdir(object_dir)
    refs_dir = os.path.join(MAIN_DIR_NAME, REFS_DIR)
    os.mkdir(refs_dir)
    open(index_file, 'a').close()
    with open(head_file, 'w') as headf:
        headf.write(f'ref: {master_ref_file}')
    open(tag_file, 'a').close()
    open(master_ref_file, 'a').close()
    if is_cvs:
        open(log_file, 'a').close()
    print('initiated')
