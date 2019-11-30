import os
import os.path as pt
import zipfile
import hashlib

CVS_DIR_NAME = '.aw'
CVS_REPOS_INFO = 'info.txt' # сюда пишется адрес репозитория? он ведь локальный!!!
CVS_REPOS_INDEX = 'index.txt'
CVS_DIR_OBJ_NAME = 'objects'

"""Узнавать время изменения файлов, чтобы понять modified, unmodified, staged"""


def add(path):
    """Добавляет файл/директорию в индексируемые, сохраняет текущие изменения в папке object"""
    """При добавлении папки рекурсивно должны добавлятся все объекты в них"""
    if pt.isdir(path):
        walk = os.walk(path)
        for root, _, files in walk:
            # print(root, _, files)
            for file in files:
                # print(pt.join(root,file))
                add(pt.join(root,file))
    index_addr = pt.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    with open(index_addr, 'r+', encoding = 'UTF-8') as index:
        if path + '\n' not in index.read():
            index.write(path + '\n')
    save_obj(path)


def save_obj(path):
    """Сохранение файла в репозитории """
    # TODO: Обработка директории
    # walk = os.walk(directory)

    # print('path: \n',path)
    splt_path = list(pt.split(path))
    print('splt_path: \n',splt_path)
    # arch_addr = pt.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME, '@'.join(splt_path) + '.zip') # Адрес получается из хэширования имени + содержимого
    header = 'blob ' + os.stat(path).st_size
    arch_addr = hash_obj(path, header)
    arch_addr = [arch_addr[0:2], arch_addr[2:]]
    arch_addr[0] = pt.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME, arch_addr[0])
    os.mkdir(arch_addr[0])
    # print(arch_addr)
    with zipfile.ZipFile(pt.join(arch_addr[0],arch_addr[1]), mode = 'w') as zp:
        zp.write(header) 
        zp.write(path) 
    # hash_obj(12)


def hash_obj(path, header):#(path: str) -> (str,str):
    """Хэшируем файл"""
    sha1 = hashlib.sha1()
    # pt.split(path)

    sha1.update(header)
    with open(path,'rb') as f:
        file_bytes = f.read()
        while file_bytes:
            sha1.update(file_bytes)
            file_bytes = f.read()
    return sha1.hexdigest()

