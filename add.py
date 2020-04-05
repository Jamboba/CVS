import os
import os.path
import zipfile
from shutil import copyfile

from atomic import get_hash_for_path

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
        return add_directory(path)

    save_file(path)
    update_index_file(path)


def add_file(current_directory, file_name):
    file_full_path = os.path.join(current_directory, file_name)
    add(file_full_path)


def add_directory(path):
    """Разбираем содержимое директории рекурсивно"""

    dir_generator = os.walk(path)
    while True:
        try:
            (directory_name,
             subdirectories,
             files_in_current_directory) = next(dir_generator)

            if len(subdirectories) > 0:
                for directory in subdirectories:
                    sub_directory_path = os.path.join(directory_name, directory)
                    add_directory(sub_directory_path)

            for file_name in files_in_current_directory:
                add_file(directory_name, file_name)
        except StopIteration:
            break


def save_file(path):
    """Сохранение файла в репозитории """

    path_hash_value = get_hash_for_path(path)
    file_directory_letters = path_hash_value[0:2]
    file_directory_path = os.path.join(
        CVS_DIR_NAME,
        CVS_DIR_OBJ_NAME,
        file_directory_letters
    )
    try:
        os.mkdir(file_directory_path)
    except FileExistsError as e:
        print(e)

    rest_hash_value_part = path_hash_value[2:]
    zip_file_path = os.path.join(file_directory_path, rest_hash_value_part)
    with zipfile.ZipFile(zip_file_path, mode='w') as zipped_file:
        archive_name = os.path.basename(path)
        zipped_file.write(path, arcname=archive_name)


# На каждый вызов этого метода идет перекопирование индекса.
# Это ебано, потому что метод вызывается на КАЖДЫЙ новый файл при добавлении.
# Предлагаю это переписать на генерацию нового индекса каждый раз:
# Зашли сюда с конкретным файлом -- просто дописали файл в конец нового файла,
# который создаем один раз.
# Это надо еще продумать, но то, как это сейчас работает, ето пиздец
def update_index_file(path):
    """Обновление индекса"""
    path_hash_value = get_hash_for_path(path)
    index_file_path = os.path.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    tmp_file_path = os.path.join(CVS_DIR_NAME, TMP_FILE)
    should_update = False

    with open(index_file_path, 'r') as index_file, \
            open(tmp_file_path, 'w') as tmp:
        while True:
            index_file_row = index_file.readline()

            if not index_file_row:
                break
            indexed_file, indexed_file_hash = index_file_row.split()

            if indexed_file == path:
                if indexed_file_hash != path_hash_value:
                    indexed_file_hash = path_hash_value
                    index_file_row = ' '.join([
                        indexed_file,
                        indexed_file_hash,
                        '\n'
                    ])
                should_update = True
            tmp.write(index_file_row)
    if should_update:
        copyfile(tmp_file_path, index_file_path)
    else:
        with open(index_file_path, 'a') as index:
            index.write(f'{path} {path_hash_value}\n')
    os.remove(tmp_file_path)
