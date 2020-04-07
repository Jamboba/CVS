import os
import os.path
import zipfile
import hashlib
import logging
from shutil import copyfile

from atomic import hash_obj
from constants import *


def add(path):
    """Добавляет файл/директорию в индексируемые,
    сохраняет текущие изменения в папке object
    параметр path - путь до добавляемого файла"""

    path = os.path.normpath(path)
    if os.path.isdir(path):
        return add_directory(path)
    add_file(path)


def add_file(path):
    """Добавление файла в индекс"""

    hashed_path = hash_obj(path)
    save_obj(path, hashed_path)
    change_index(path, hashed_path)


def add_directory(path):
    """Разбираем содержимое директории нерекурсивно(!)"""

    dir_generator = os.walk(path)
    while True:
        try:
            curr_path, _, files = next(dir_generator)
            for file in files:
                fullpath = os.path.join(curr_path, file)
                add_file(fullpath)
        except StopIteration:
            break


def save_obj(path, file_hash):
    """Сохранение файла в репозитории """

    splt_path = list(os.path.split(path))
    file_dir = os.path.join(MAIN_DIR_NAME, OBJ_DIR_NAME, file_hash[0:2])
    file_name = file_hash[2:]
    try:
        os.mkdir(file_dir)
    except FileExistsError as e:
        logging.exception(e)
    with zipfile.ZipFile(
            os.path.join(file_dir, file_name), mode='w') as zp:
        zp.write(path, arcname=splt_path[1])


def change_index(path, hashed_path):
    """Обновление индекса"""

    index_addr = os.path.join(MAIN_DIR_NAME, REPOS_INDEX)
    tmp_file = os.path.join(MAIN_DIR_NAME, TMP_FILE)
    is_indexed = False
    with open(index_addr, 'r') as index, open(tmp_file, 'w') as tmp:
        while True:
            index_line = index.readline()
            if not index_line:
                break
            index_path, index_hash = index_line.split()
            if index_path == path:
                if index_hash != hashed_path:
                    index_hash = hashed_path
                    index_line = ' '.join([index_path, index_hash])
                is_indexed = True
            tmp.write(index_line + '\n')

    if is_indexed:
        copyfile(tmp_file, index_addr)
    else:
        with open(index_addr, 'a') as index:
            index.write(f'{path} {hashed_path}\n')
    os.remove(tmp_file)
