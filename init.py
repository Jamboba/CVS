import os
import os.path as pt
import pathlib
import sys
import hashlib #
import zipfile



import add
import commit



# TODO: Реализовать локальную систему контроля версий с базовыми операциями (init, add, commit, reset, log)


# TODO: обработка ошибок
# TODO: обработка команд работы с директорией
# TODO: Сохранение номера версии
# TODO: Игнорирование файлов .awignore
# TODO: diff, просматриваем файлы с одинаковым названием попарно построчно, если строки не совпадают
"""как это работает:
пользователь через консоль запускает программу в формате 
awCVS [init, commit, checkout(следующий аргумент номер версии)] имя_директории, которую сохраняем
парсим аргументы командной строки, в директории ищем папку .aw, если ее нет, то создаем, в ней адрес репозитория, 

Консольная версия
1. Реализация на основе [что-то одно]:
    Хранение файлов
    Хранение диффов 
2. Реализация базовых операций: init, add, commit, checkout, reset, log, branch
3. добавление файлов/каталогов (add) 
4. коммит изменений (commit)
5. перемещение между версиями (checkout)
6. просмотр лога (список изменённых файлов + время) (log)
7. Теги (tag ???)
8. Просмотр списка коммитов/тегов для перемещения между ними
9. Сообщения в коммитах, в тегах
10. Создание веток и простейшие операции с ними (без слияния)
"""


CVS_DIR_NAME = '.aw'
CVS_REPOS_INFO = 'info.txt' # сюда пишется адрес репозитория? он ведь локальный!!!
CVS_REPOS_INDEX = 'index.txt'
CVS_DIR_OBJ_NAME = 'objects'
CVS_DIR_TEMP = 'tmp'
CVS_IGNORE_FILE = '.awignore.txt'

def init():
    """ Создает папку .aw в директории, с которой будем работать,
        записываем  """
    os.mkdir(CVS_DIR_NAME)
    object_dir = pt.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME)
    os.mkdir(object_dir)
    temp_dir = pt.join(CVS_DIR_NAME,CVS_DIR_TEMP)
    os.mkdir(temp_dir)
    ignore_adr = pt.join(CVS_DIR_NAME, CVS_IGNORE_FILE)
    index_addr = pt.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    with open(index_addr, 'w', encoding = 'UTF-8'):
        pass
    with open(ignore_adr, 'w', encoding = 'UTF-8'):
        print("initiated")
    

def diff():
    pass

def reset():
    pass


def log():
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
    "reset": reset,
    "log": log
}

main()
