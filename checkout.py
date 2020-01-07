import os
import os.path as pt
import zipfile

import add
from commit import write_ref

CVS_DIR_NAME = '.aw'
CVS_REPOS_INFO = 'info.txt'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'


TXT_EXTENSION = '.txt'
ROOT_DIR = '.'
COMMITS_DIR = 'commits'
TAG_FILE = 'tag'
REFS_DIR = 'refs'
HEAD_FILE = 'head'


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
    ref_file = pt.join(CVS_DIR_NAME, REFS_DIR, name)
    if os.path.exists(ref_file):
        with open(ref_file, 'r') as f:
            commit_hash = f.read().strip()
        return commit_hash
    else:
        return


def is_tag(name):
    """Возвращает коммит, на который указывает тег, если передан тег"""
    tag_file = pt.join(CVS_DIR_NAME, TAG_FILE)
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
    head_file = pt.join(CVS_DIR_NAME, HEAD_FILE)
    name_ref = pt.join(CVS_DIR_NAME, REFS_DIR, name)
    with open(head_file, 'w') as f:
        # print(f'ref: {name_ref}', file=f)
        f.write(f'ref: {name_ref}')


def update_catalog_and_index(commit_name):
    commit_file_path = pt.join(
                            CVS_DIR_NAME,
                            CVS_DIR_OBJ_NAME,
                            commit_name[0:2],
                            commit_name[2:])
    with open(commit_file_path, 'r') as commit:
        update_index = []
        while True:
            file_info = commit.readline()
            if not file_info:
                break
            update_index.append(file_info)
            file_info = file_info.split(' ')
            filename = pt.split(file_info[0])
            zip_path = pt.join(
                CVS_DIR_NAME,
                CVS_DIR_OBJ_NAME,
                file_info[1][:2], file_info[1][2:-1])
            target_path = pt.join(ROOT_DIR, filename[0])
            with zipfile.ZipFile(zip_path, mode='r') as zp:
                zp.extract(filename[1], target_path)
    index_path = pt.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    diff(commit_file_path, index_path)
    print('update_index', update_index)
    with open(index_path, 'w') as index:
        for i in update_index:
            # print(i, file=index)
            index.write(i)


def diff(new_index_path, old_index_path):
    """Расчитывает разницу между старым и новым индексом"""
    with open(new_index_path) as new:
        files_new = {i.split(' ')[0] for i in new.readlines() if i != '\n'}
    print('new_index', files_new)
    with open(old_index_path) as old:
        files_old = {i.split(' ')[0] for i in old.readlines() if i != '\n'}
    print('old_index', files_old)

    if files_new.issubset(files_old):
        delete_files(files_old-files_new)


def delete_files(files):
    """Удаляет разницу между коммитами"""
    print(files)
    for file in files:
        os.remove(file)
