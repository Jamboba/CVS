import os
import zipfile
import pathlib
import sys

CVS_DIR_NAME = '\\.aw'
CVS_REPOS_INFO = '\\info.txt'

# TODO: Реализовать локальную систему контроля версий с базовыми операциями (init, add, commit, reset, log)
# TODO: обработка ошибок
# TODO: обработка команд работы с директорией
# TODO: Сохранение номера версии
"""как это работает:
пользователь через консоль запускает программу в формате 
awCVS [init, commit, checkout(следующий аргумент номер версии)] имя_директории, которую сохраняем
парсим аргументы командной строки, в директории ищем папку .aw, если ее нет, то создаем, в ней адрес репозитория, 
"""
"""
Консольная версия
Реализация базовых операций: init, add, commit, reset, log
добавление файлов/каталогов
коммит изменений
перемещение между версиями
просмотр лога (список изменённых файлов + время)
Реализация на основе [что-то одно]:
Хранение файлов
Хранение диффов
Теги
Просмотр списка коммитов/тегов для перемещения между ними
Сообщения в коммитах, в тегах
Создание веток и простейшие операции с ними (без слияния)
"""


def init(directory, repository):
    """ Создает папку .aw в директории, с которой будем работать,
        записываем  """
    info_dir = directory + CVS_DIR_NAME
    pathlib.Path(info_dir).mkdir(exist_ok=True)
    with open (info_dir + CVS_REPOS_INFO, 'w') as f:
        f.write(repository)
    print("initiated")


def add():
    print("add")


def commit(directory):
    """Сохраняем ВСЮ директорию"""
    info_file = directory+ CVS_DIR_NAME + CVS_REPOS_INFO
    repos_address = ""
    with open (info_file, 'r') as f:
        repos_address = f.read()

    dir_name = "\\"+str(pathlib.Path(directory).name)

    walk = os.walk(directory)
    with zipfile.ZipFile(repos_address + dir_name + '.zip', mode='w') as zp:
        for root,_,files in walk:
            for file in files:
                zp.write(root+'\\'+file,(root+'\\'+file)[len(directory):])

    print('SUCCESS')

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
