import os
import os.path as pt
import zipfile
import hashlib

CVS_DIR_NAME = '.aw'
CVS_REPOS_INFO = 'info.txt' # сюда пишется адрес репозитория? он ведь локальный!!!
CVS_REPOS_INDEX = 'index.txt'
CVS_DIR_OBJ_NAME = 'objects'
CVS_BLOB_OBJ = 'blob'
CVS_DIR_TEMP = 'tmp'



def add(path):
    """Добавляет файл/директорию в индексируемые, сохраняет текущие изменения в папке object"""
    """При добавлении папки рекурсивно должны добавлятся все объекты в них"""
    if pt.isdir(path):
        add_tree(path)
    index_addr = pt.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    hash = hash_obj(path)
    save_obj(path,hash)
    # if not obj_hash: return
    with open(index_addr, 'a', encoding = 'UTF-8') as index:
        # if path + '\n' not in index.read():
        # index.write(CVS_BLOB_OBJ + path + obj_hash + '\n')
        print(f'{CVS_BLOB_OBJ} {hash} {path} \n')
        index.write(f'{CVS_BLOB_OBJ} {hash} {path} \n')
    return path,hash
    


def save_obj(path, hash):
    """Сохранение файла в репозитории """

    splt_path = list(pt.split(path))
    print('splt_path: \n',splt_path)
    # header = 'blob ' + os.stat(path).st_size
    #aarch_addr = hash_obj(path, header)
    arch_addr = hash
    # hash_to_send = arch_addr
    arch_addr = [arch_addr[0:2], arch_addr[2:]]
    print(arch_addr)
    arch_addr[0] = pt.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME, arch_addr[0])
    try:
        os.mkdir(arch_addr[0])
    except FileExistsError as e:
        print(e)
        # return
    with zipfile.ZipFile(pt.join(arch_addr[0],arch_addr[1]), mode = 'w') as zp:
        # zp.write(header) 
        zp.write(path) 
    # hash_obj(12)
    # return hash_to_send
    


def hash_obj(path):#(path: str) -> (str,str):
    """Хэшируем файл"""
    sha1 = hashlib.sha1()
    with open(path,'rb') as f:
        file_bytes = f.read()
        while file_bytes:
            sha1.update(file_bytes)
            file_bytes = f.read()
    return sha1.hexdigest()


def add_tree(path):
    walk = os.walk(path, topdown=False)
     # блобы, входящие в новое дерево
    for root, dirs, files in walk:
        for dir in dirs:
            #из за того что обходим снизу вверх, все вложенные папки уже обработаны,
            #нужно только добавить их названия и хэши в файл
        inner_files = {}
        for file in files:
            blob = pt.join(root,file)
            hash = add(blob)[1] 
            file_type = CVS_BLOB_OBJ
            inner_files[file_type,file] = hash
        write_tree(root, inner_files)
            # теперь этот файл будет сохранен, но не связан с деревом
            """Чтобы записать дерево, все входящие в него части должны быть уже захэшированы
            значит деревья должны хешироватся с самого начала"""
def write_tree(dir, inner_files):
    with open (pt.join(CVS_DIR_NAME,CVS_DIR_TEMP), mode='w') as dir_file:
        for key, value in inner_files.items():
            dir_file.write(f'{key[0]} {value} {key[1]} \n')


    """"сохраняет файл, с названием директории, в котором
    записаны название блобов, их хешей, и деревьев, которые в него вхожят
    """

# def write_tree():
#     """создание объекта дерева из индекса
#     В дереве могут хранится ссылки на блобы и ссылки на другие деревья"""
#     with open (CVS_DIR_NAME + CVS_REPOS_INDEX, 'r') as index:
#         with open 
