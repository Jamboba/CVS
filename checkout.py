import os
import os.path
import zipfile

import add
from constants import *
from atomic import write_ref, update_catalog_and_index


def checkout(target):
    """ Принимает ветку, коммит, тег
        Изменяет состояние директории
        Перемещает HEAD на новую ветку"""
    check_tag = is_tag(target)
    check_branch = is_branch(target)
    print(check_tag)
    if check_tag:
        target = check_tag
    elif check_branch:
        write_head(target)
        target = check_branch
    else:
        write_ref(target)
    update_catalog_and_index(target)


def is_branch(name):
    """Возвращает коммит, на который указывает ветка, если передана ветка"""
    ref_file = os.path.join(MAIN_DIR_NAME, REFS_DIR, name)
    if os.path.exists(ref_file):
        with open(ref_file, 'r') as f:
            commit_hash = f.read().strip()
        return commit_hash
    else:
        return


def is_tag(name):
    """Возвращает коммит, на который указывает тег, если передан тег"""
    tag_file = os.path.join(MAIN_DIR_NAME, TAG_FILE)
    with open(tag_file, 'r') as tagf:
        tag_list = tagf.readlines()
        try:
            tagging_commit = list(filter(
                lambda x: x.split(' ')[0].find(name) > -1, tag_list))[0]
            return tagging_commit.split(' ')[1].strip()
        except IndexError as e:
            print('Не тег')
            return


def write_head(name):
    head_file = os.path.join(MAIN_DIR_NAME, HEAD_FILE)
    name_ref = os.path.join(MAIN_DIR_NAME, REFS_DIR, name)
    with open(head_file, 'w') as f:
        f.write(f'ref: {name_ref}')
