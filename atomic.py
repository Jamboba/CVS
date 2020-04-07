import hashlib
import os
import os.path
import time

from constants import *


"""Функции, которые используется несколькими модулями"""


def hash_obj(path):
    """Хэшируем файл"""
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        file_bytes = f.read()
        while file_bytes:
            sha1.update(file_bytes)
            file_bytes = f.read()
    return sha1.hexdigest()


def add_log(commit_hash):
    """Получает полный хэш коммита"""

    log_file = os.path.join(MAIN_DIR_NAME, LOG_FILE)
    commit_path = os.path.join(
        MAIN_DIR_NAME,
        OBJ_DIR_NAME,
        commit_hash[0:2],
        commit_hash[2:])
    commit_create_time = time.ctime(os.path.getctime(commit_path))
    with open(log_file, 'a') as log:
        print(f'commit: {commit_hash}', file=log)
        print(f'Data: {commit_create_time}', file=log)


def update_catalog_and_index(commit_name):
    commit_file_path = pt.join(
                MAIN_DIR_NAME,
                OBJ_DIR_NAME,
                commit_name[0:2],
                commit_name[2:]
                )
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
                MAIN_DIR_NAME,
                OBJ_DIR_NAME,
                file_info[1][:2],
                file_info[1][2:-1]
                )
            target_path = pt.join(ROOT_DIR, filename[0])
            with zipfile.ZipFile(zip_path, mode='r') as zp:
                zp.extract(filename[1], target_path)
    index_path = pt.join(MAIN_DIR_NAME, REPOS_INDEX)
    diff(commit_file_path, index_path)
    print('update_index', update_index)
    with open(index_path, 'w') as index:
        for i in update_index:
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


def write_ref(hash):
    head_file = os.path.join(MAIN_DIR_NAME, HEAD_FILE)
    with open(head_file, 'r') as head:
        ref = head.read().split(' ')[1].strip()
    with open(ref, 'w') as rf:
        print(hash, file=rf)
