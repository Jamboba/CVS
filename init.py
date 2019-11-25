import os
import zipfile
import pathlib
import sys


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
"""
"""
Консольная версия
1. Реализация на основе [что-то одно]:
    Хранение файлов
    Хранение диффов 
2. Реализация базовых операций: init, add, commit, reset, log
3. добавление файлов/каталогов
4. коммит изменений
5. перемещение между версиями
6. просмотр лога (список изменённых файлов + время)
7. Теги
8. Просмотр списка коммитов/тегов для перемещения между ними
9. Сообщения в коммитах, в тегах
10. Создание веток и простейшие операции с ними (без слияния)
"""


CVS_DIR_NAME = '\\.aw'
CVS_REPOS_INFO = '\\info.txt'


def init(directory, repository):
    # Директория должна быть равна репозиторию?
    # Репозиторий .aw?
    """ Создает папку .aw в директории, с которой будем работать,
        записываем  """
    info_dir = directory + CVS_DIR_NAME
    pathlib.Path(info_dir).mkdir(exist_ok = True)
    with open(info_dir + CVS_REPOS_INFO, 'w') as f:
        f.write(repository)
    print("initiated")


def add(file_path):
    """Добавляет файл в отслеживаемые(индексируемые)"""

    with open(file_path, 'w') as index:
        pass

def commit(directory):
    """Сейчас: Сохраняем ВСЮ директорию
        Должно быть: фиксация изменений в проиндексированных(файл index) файлах, если есть флаг -а, то все отслеживаемые(?) на
        момент коммита"""
    info_file = directory + CVS_DIR_NAME + CVS_REPOS_INFO
    repos_address = ""
    with open(info_file, 'r') as f:
        repos_address = f.read()

    dir_name = "\\"+str(pathlib.Path(directory).name)

    walk = os.walk(directory)
    with zipfile.ZipFile(repos_address + dir_name + '.zip', mode='w') as zp:
        for root, _, files in walk:
            for file in files:
                zp.write(root+'\\'+file, (root+'\\'+file)[len(directory):])

    print('SUCCESS')

def diff():


def reset():
    pass


def log():
    pass


def main():
    # print(functions)
    functions[sys.argv[1]](*sys.argv[2:])


functions = {
    "init": init,
    "add": add,
    "commit": commit,
    "reset": reset,
    "log": log
}

main()
