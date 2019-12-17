import os
import os.path as pt
import zipfile
import hashlib


CVS_DIR_NAME = '.aw'
CVS_REPOS_INFO = 'info.txt'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
CVS_BLOB_OBJ = 'blob'
CVS_TREE_OBJ = 'tree'
CVS_DIR_TEMP = 'tmp'
TXT_EXTENSION = '.txt'


""""При добавлении папки объект дерева не создается"""


def add(path, typeof = CVS_BLOB_OBJ, dir_path = None):
    """Добавляет файл/директорию в индексируемые, сохраняет текущие изменения в папке object"""
    #print('adding ',path)
    if pt.isdir(path):
        print('it"s directory')
        return add_tree(path)
    index_addr = pt.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    hash = hash_obj(path)
    save_obj(path,hash)

    """Индекс записывается немного иначе:
    Когда добавляется папка, в индекс записываются входящие в нее файлы
    """
    index_content = ''

    with open(index_addr, 'r', encoding = 'UTF-8') as index:
        index_content = index.readlines()
    print("index_content before", index_content)
    check_change = False
    if index_content:
        for i in index_content:
            print('was',i)
            file_info = i.split(' ')
            if file_info[0] == path:
                print ('HASH', hash)
                file_info[1] = hash.strip()
                check_change = True
                index_content[index_content.index(i)]=' '.join(file_info)+'\n'
                break
            print('bec',i)
    print("index_content after",index_content)
    print(f'{path} {hash}')
    if check_change:
        with open(index_addr, 'w', encoding = 'UTF-8') as index:
            print('test tut')
            for i in index_content:
                index.write(i)
    else:
        with open(index_addr, 'a', encoding = 'UTF-8') as index:
            print(f'{path} {hash}', file=index)
    return typeof, hash, path
    


def save_obj(path, hash):
    """Сохранение файла в репозитории """

    splt_path = list(pt.split(path))
    #print('splt_path: \n',splt_path)
    arch_addr = hash
    arch_addr = [arch_addr[0:2], arch_addr[2:]]
    #print('hashed obj:',arch_addr)
    arch_addr[0] = pt.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME, arch_addr[0])
    try:
        os.mkdir(arch_addr[0])
    except FileExistsError as e:
        print(e)
    with zipfile.ZipFile(pt.join(arch_addr[0],arch_addr[1]+'.zip'), mode = 'w') as zp:
        zp.write(path, arcname = splt_path[1])

    


def hash_obj(path):#(path: str) -> (str,str):
    """Хэшируем файл"""
  #  print('this path ', path)
    sha1 = hashlib.sha1()
    with open(path,'rb') as f:
        file_bytes = f.read()
        while file_bytes:
            sha1.update(file_bytes)
            file_bytes = f.read()
    return sha1.hexdigest()


def add_tree(path, commit=False):
    """Разбираем содержимое директории рекурсивно"""
    objects = os.listdir(path)
    inner_files = {}
    for obj in objects:
        fullpath = pt.join(path,obj)
        if pt.isdir(fullpath): 
            inner_files[fullpath] = add_tree(fullpath) # возвращается кортеж type, hash, path
        else: 
            inner_files[fullpath] = add(fullpath) # возвращается кортеж type, hash, path (blob, 4g343gddsserthj, /kek/lol/text.txt)

    print(inner_files)
    if commit:
        return save_tree(path,inner_files)

""""Должно возвращать:(tree, хэш, название)"""

def save_tree(path,inner_files):
    """Сохраняем временный файл, который отражает содержимое директории
        Дерево должно cохранять  относительный путь файлов
    """
    print("Saving tree ",path," with ", inner_files)
    dir_name = pt.basename(path)
    temp_file = pt.join(CVS_DIR_NAME,CVS_DIR_TEMP,dir_name + TXT_EXTENSION)
    with open (temp_file, mode='w') as dir_file:
        for obj_path, info in inner_files.items():
            string = f'{info[0]} {info[1]} {pt.basename(obj_path)} \n'
            dir_file.write(string)
    return add(temp_file, typeof=CVS_TREE_OBJ, dir_path=path)
