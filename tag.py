# import os
# import os.path

from constants import *


def tag(name=None, commit_hash=None):
    """Без аргументов показывает все тэги
        с именем - именует последний коммит
        с именем и хэшем - именует коммит соответсвующий хэшу"""

    if not name:
        show_tag()
        return
    if not commit_hash:
        with open(head_file, 'r') as f:
            ref = f.read().split(' ')[1].strip()
        with open(ref, 'r') as f:
            commit_hash = f.read()[:-1]
    # Проверка на то что запись уже существует
    with open(tag_file, 'a') as tag:
        tag.write(f'{name} {commit_hash}\n')
    with open(log_file, 'r') as log:
        log_list = log.readlines()
        tagging_commit = list(filter(
            lambda x: x.find(commit_hash) > -1, log_list))[0]
        log_list[log_list.index(tagging_commit)] =\
            f'{tagging_commit[:-1]} {TAG_FILE}: {name}\n'
    with open(log_file, 'w') as log:
        for string in log_list:
            log.write(string)


def show_tag():
    with open(tag_file, 'r') as tagf:
        print(tagf.read())
