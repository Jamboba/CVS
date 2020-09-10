import os.path
import zipfile
import logging
from shutil import copyfile

from atomic import hash_obj
from constants import *


def add(path):
    """Добавляет файл/директорию в индекс,
    сохраняет текущие изменения в папке object
    параметр path - путь до добавляемого файла/папки"""

    path = os.path.normpath(path)
    if os.path.isdir(path):
        return add_directory(path)
    add_file(path)


def add_file(file_path):
    """Добавление файла в индекс"""

    hashed_path = hash_obj(file_path)
    save_obj(file_path, hashed_path)
    change_index(file_path, hashed_path)


def add_directory(dir_path):
    """Разбираем содержимое директории нерекурсивно(!)"""

    dir_generator = os.walk(dir_path)
    while True:
        try:
            curr_path, _, files = next(dir_generator)
            for file in files:
                fullpath = os.path.join(curr_path, file)
                add_file(fullpath)
        except StopIteration:
            break


def save_obj(file_path, file_hash):
    """Сохранение файла в репозитории """

    splt_path = list(os.path.split(file_path))
    file_dir = os.path.join(MAIN_DIR_NAME, OBJ_DIR_NAME, file_hash[0:2])
    file_name = file_hash[2:]
    try:
        os.mkdir(file_dir)
    except FileExistsError as e:
        logging.exception(e)
    with zipfile.ZipFile(
            os.path.join(file_dir, file_name), mode='w') as zp:
        zp.write(file_path, arcname=splt_path[1])


def change_index(file_path, hashed_path):
    """Обновление индекса"""

    is_file_indexed = False
    with open(index_file, 'r') as index, open(tmp_file, 'w') as tmp:
        while True:
            index_line = index.readline()
            if not index_line:
                break
            index_file_path, index_file_hash = index_line.split()
            if index_file_path == file_path:
                if index_file_hash != hashed_path:
                    index_line = ' '.join([file_path, hashed_path + '\n'])
                is_file_indexed = True
            tmp.write(index_line)

    if is_file_indexed:
        copyfile(tmp_file, index_file)
    else:
        with open(index_file, 'a') as index:
            index.write(f'{file_path} {hashed_path}\n')
    os.remove(tmp_file)
