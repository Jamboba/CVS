import os
import os.path

CVS_DIR_NAME = '.aw'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
HEAD_FILE = 'head'
LOG_FILE = 'log'
TAG_FILE = 'tag'


def tag(name=None, commit_hash=None):
    """Без аргументов показывает все тэги
        с именем - именует последний коммит
        с именем и хэшем - именует коммит соответсвующий хэшу"""
    if not name:
        show_tag()
        return
    if not commit_hash:
        head_file = os.path.join(CVS_DIR_NAME, HEAD_FILE)
        with open(head_file, 'r') as f:
            ref = f.read().split(' ')[1].strip()
        with open(ref, 'r') as f:
            commit_hash = f.read()[:-1]
    tag_file = os.path.join(CVS_DIR_NAME, TAG_FILE)
    # Проверка на то что запись уже существует
    with open(tag_file, 'a') as tag:
        # print(f'{name} {commit_hash}', file=tag)
        tag.write(f'{name} {commit_hash}\n')
    log_file = os.path.join(CVS_DIR_NAME, LOG_FILE)
    with open(log_file, 'r') as log:
        log_list = log.readlines()
        print('log list:', log_list)
        print(commit_hash)
        print('53957e9eab8f0814b154f160f5bf938cd56d944d')
        print(log_list[0].find(commit_hash))
        print(log_list[0].find('53957e9eab8f0814b154f160f5bf938cd56d944d'))
        tagging_commit = list(filter(
            lambda x: x.find(commit_hash) > -1, log_list))[0]
        print(tagging_commit)
        
        log_list[log_list.index(tagging_commit)] =\
            f'{tagging_commit[:-1]} {TAG_FILE}: {name}\n'
    with open(log_file, 'w') as log:
        for string in log_list:
            log.write(string)


def show_tag():
    tag_file = os.path.join(CVS_DIR_NAME, TAG_FILE)
    with open(tag_file, 'r') as tagf:
        print(tagf.read())
