import os
import os.path
import zipfile
import hashlib

from atomic import hash_obj

CVS_DIR_NAME = '.aw'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'


def add(path):
    """Добавляет файл/директорию в индексируемые,
    сохраняет текущие изменения в папке object"""
    path = os.path.normpath(path)

    if os.path.isdir(path):
        return add_tree(path)
    index_addr = os.path.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    hashed_path = hash_obj(path)
    save_obj(path, hashed_path)
    index_content = ''
    with open(index_addr, 'r') as index:
        index_content = index.readlines()
    check_change = False

    if index_content:
        for i in index_content:
            file_info = i.split(' ')
            # index_path, index_hash = index_line.split()
            if file_info[0] == path:
                file_info[1] = hashed_path.strip()
                check_change = True
                index_content[index_content.index(i)] =\
                    ' '.join(file_info)+'\n'
                break
            
    if check_change:
        with open(index_addr, 'w') as index:
            for i in index_content:
                index.write(i)
    else:
        with open(index_addr, 'a') as index:
            index.write(f'{path} {hashed_path}\n')


def save_obj(path, file_hash):
    """Сохранение файла в репозитории """

    splt_path = list(os.path.split(path))
    arch_addr = file_hash
    arch_addr = [arch_addr[0:2], arch_addr[2:]]
    arch_addr[0] = os.path.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME, arch_addr[0])
    try:
        os.mkdir(arch_addr[0])
    except FileExistsError as e:
        print(e)
    with zipfile.ZipFile(
                os.path.join(arch_addr[0], arch_addr[1]),
                mode='w') as zp:
        zp.write(path, arcname=splt_path[1])


def add_tree(path, commit=False):
    """Разбираем содержимое директории рекурсивно"""
    objects = os.listdir(path)
    for obj in objects:
        fullpath = os.path.join(path, obj)
        if os.path.isdir(fullpath):
            add_tree(fullpath)
        else:
            add(fullpath)
