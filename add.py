import os
import os.path
import zipfile
import hashlib
from shutil import copyfile

from atomic import hash_obj

CVS_DIR_NAME = '.aw'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
TMP_FILE = 'tmp'


def add(path):
    """Добавляет файл/директорию в индексируемые,
    сохраняет текущие изменения в папке object
    параметр path - путь до добавляемого файла"""

    path = os.path.normpath(path)

    if os.path.isdir(path):
        return add_tree(path)

    hashed_path = hash_obj(path)
    save_obj(path, hashed_path)
    change_index(path, hashed_path)


def add_tree(path):
    """Разбираем содержимое директории рекурсивно"""

    dir_generator = os.walk(path)
    while True:
        try:
            dir_content = next(dir_generator)
            curr_path = dir_content[0]
            files = dir_content[2]
            for file in files:
                fullpath = os.path.join(curr_path, file)
                add(fullpath)
        except StopIteration:
            break


def save_obj(path, file_hash):
    """Сохранение файла в репозитории """

    splt_path = list(os.path.split(path))
    arch_addr = file_hash
    arch_addr = [arch_addr[0:2], arch_addr[2:]]
    file_dir = arch_addr[0]
    file_dir = os.path.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME, file_dir)
    try:
        os.mkdir(arch_addr[0])
    except FileExistsError as e:
        print(e)
    with zipfile.ZipFile(
            os.path.join(arch_addr[0], arch_addr[1]), mode='w') as zp:
        zp.write(path, arcname=splt_path[1])


def change_index(path, hashed_path):
    """Обновление индекса"""

    index_addr = os.path.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    tmp_file = os.path.join(CVS_DIR_NAME, TMP_FILE)
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
                is_indexed = True
            index_line = ' '.join([index_path, index_hash])
            tmp.write(index_line + ' \n')
    if is_indexed:
        copyfile(tmp_file, index_addr)
    else:
        with open(index_addr, 'a') as index:
            index.write(f'{path} {hashed_path}\n')
    os.remove(tmp_file)
