import os
import os.path as pt
import pathlib
import sys
import hashlib 
import zipfile
import argparse



import add
import commit
import checkout
import log
import tag 
import branch

# TODO: Реализовать локальную систему контроля версий с базовыми операциями (init, add, commit, reset, log)


# TODO: обработка ошибок
# TODO: обработка команд работы с директорией
# TODO: Сохранение номера версии
# TODO: Игнорирование файлов .awignore
# TODO: diff, просматриваем файлы с одинаковым названием попарно построчно, если строки не совпадают
"""
Консольная версия
1. Реализация на основе [что-то одно]:
    Хранение файлов
    Хранение диффов 
2. Реализация базовых операций: init, add, commit, checkout, reset, log, branch
3. добавление файлов/каталогов (add) 
4. коммит изменений (commit)
5. перемещение между версиями (checkout)
6. просмотр лога (список изменённых файлов + время) (log)
7. Теги 
8. Просмотр списка коммитов/тегов для перемещения между ними
9. Сообщения в коммитах, в тегах
10. Создание веток и простейшие операции с ними (без слияния)
"""


CVS_DIR_NAME = '.aw'
CVS_REPOS_INFO = 'info.txt' # сюда пишется адрес репозитория? он ведь локальный!!!
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
CVS_DIR_TEMP = 'tmp'
# CVS_IGNORE_FILE = '.awignore.txt'
HEAD_FILE = 'head'
LOG_FILE = 'log'
TAG_FILE = 'tag'
REFS_DIR = 'refs'
MASTER_REF_FILE ='master'



def init():
    """ Создает папку .aw в директории, с которой будем работать,
        записываем  """
    os.mkdir(CVS_DIR_NAME)
    object_dir = pt.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME)
    os.mkdir(object_dir)
    temp_dir = pt.join(CVS_DIR_NAME,CVS_DIR_TEMP)
    os.mkdir(temp_dir)
    refs_dir = pt.join(CVS_DIR_NAME,REFS_DIR)
    os.mkdir(refs_dir)
    master_ref = pt.join(CVS_DIR_NAME, REFS_DIR, MASTER_REF_FILE)
    head_file = pt.join(CVS_DIR_NAME,HEAD_FILE)
    # ignore_adr = pt.join(CVS_DIR_NAME, CVS_IGNORE_FILE)
    index_file = pt.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    log_file = pt.join(CVS_DIR_NAME, LOG_FILE)
    tag_file = pt.join(CVS_DIR_NAME, TAG_FILE)
    open(index_file,'a').close()
    # open(ignore_adr,'a').close()
    with open(head_file, 'w') as headf:
        print(f'ref: {master_ref}',file=headf)

    open(log_file,'a').close()
    open(tag_file,'a').close()
    open(master_ref,'a').close()
    # with open(index_addr, 'w', encoding = 'UTF-8'):
    #     pass
    print('initiated')

def diff():
    pass

def reset():
    pass


def make_tree():
    """Создает дерево по файлам из индекса"""
    pass


def main():
    functions[sys.argv[1]](*sys.argv[2:])


functions = {
    "init": init,
    "add": add.add,
    "commit": commit.commit,
    "checkout": checkout.checkout,
    "reset": reset,
    "log": log.log,
    "tag": tag.tag,
    "branch": branch.branch
}

main()
