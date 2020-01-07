import os
import os.path as pt
import zipfile
import hashlib


CVS_DIR_NAME = '.aw'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'


def add(path):
    """Добавляет файл/директорию в индексируемые,
    сохраняет текущие изменения в папке object"""
    if path[:2] == '.\\':
        path = path[2:]
    if pt.isdir(path):
        if path[-1] == '\\':
            path = path[:-1]
        return add_tree(path)
    index_addr = pt.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    hash = hash_obj(path)
    save_obj(path, hash)
    index_content = ''
    with open(index_addr, 'r') as index:
        index_content = index.readlines()
    check_change = False
    if index_content:
        for i in index_content:
            file_info = i.split(' ')
            if file_info[0] == path:
                file_info[1] = hash.strip()
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
            index.write(f'{path} {hash}\n')


def save_obj(path, hash):
    """Сохранение файла в репозитории """

    splt_path = list(pt.split(path))
    arch_addr = hash
    arch_addr = [arch_addr[0:2], arch_addr[2:]]
    arch_addr[0] = pt.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME, arch_addr[0])
    try:
        os.mkdir(arch_addr[0])
    except FileExistsError as e:
        print(e)
    with zipfile.ZipFile(
                pt.join(arch_addr[0], arch_addr[1]),
                mode='w'
                ) as zp:
        zp.write(path, arcname=splt_path[1])


def hash_obj(path):
    """Хэшируем файл"""
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        file_bytes = f.read()
        while file_bytes:
            sha1.update(file_bytes)
            file_bytes = f.read()
    return sha1.hexdigest()


def add_tree(path, commit=False):
    """Разбираем содержимое директории рекурсивно"""
    objects = os.listdir(path)
    for obj in objects:
        fullpath = pt.join(path, obj)
        if pt.isdir(fullpath):
            add_tree(fullpath)
        else:
            add(fullpath)
