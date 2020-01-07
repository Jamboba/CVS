import socket
import os
import os.path as pt
import sys
import time
import checkout

SERVER_ADDR = ('DESKTOP-MTLNPN0', 1337)
CVS_DIR_NAME = '.aw'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
HEAD_FILE = 'head'
LOG_FILE = 'log'
TAG_FILE = 'tag'
REFS_DIR = 'refs'
MASTER_REF_FILE = 'master'
FILE_PATH_CODE = '01'
PUSH_TAG_CODE = '02'
PUSH_BRANCH_CODE = '03'
PULL_COMMIT_CODE = '10'
PULL_TAG_CODE = '11'


def pull(target, change=False):
    """Разбирается что передано(тег, коммит, ветка).
    Пересылает связанные файлы, с директориями
    (файл индекса,файлы в индексе,структуру)
    """
    check_tag = checkout.is_tag(target)
    check_branch = checkout.is_branch(target)
    if check_tag:
        pull_tag(target, change)
    elif check_branch:
        pull_branch(target, change)
    else:
        pull_commit(target, change)


def pull_tag(tag, change=False):
    client_socket = socket.socket()
    client_socket.connect(SERVER_ADDR)
    client_socket.send(bytes(PULL_TAG_CODE, 'UTF-8') + bytes(tag, 'UTF-8'))
    # client_socket.settimeout(5)
    

def pull_branch(branch, change=False):
    pass


def pull_commit(commit, change=False):
    """Отправляет хеш коммита, получает все необходимые файлы.
    Выставляет текущую версию проекта на данный коммит"""

    client_socket = socket.socket()
    client_socket.connect(SERVER_ADDR)
    client_socket.send(bytes(PULL_COMMIT_CODE, 'UTF-8') + bytes(commit, 'UTF-8'))
    client_socket.settimeout(5)
    while True:

        full_msg = client_socket.recv(4096)
        print('байты полного сообщения:', full_msg)
        full_msg = full_msg.decode('UTF-8')

        print('full_msg', full_msg)
        if full_msg[:2] == FILE_PATH_CODE:
            print('here')
            size = client_socket.recv(4096)
            print(size)
            file_size = int(size.decode('UTF-8')[2:])
            download_file(full_msg[2:], client_socket, file_size)
    if change:
        checkout.checkout(commit)


def download_file(file_path, socket, size):
    # file_path = pt.join(SCRIPT_DIR, file_path)
    print('Загружаем файл', file_path)
    splitted_path = os.path.split(file_path)
    os.makedirs(splitted_path[0], exist_ok=True)
    print('file_path', file_path)
    with open(file_path, 'wb') as file:
        print(size+2)
        data = socket.recv(size+2)[2:]
        print('data', data)
        file.write(data)


def push(target):
    """Разбирается что передано(тег, коммит, ветка).
    Пересылает связанные файлы, с директориями(
                                                файл коммита,
                                                файлы в коммите,
                                                структуру)
    """
    if checkout.is_tag(target):
        push_tag(target)
    elif checkout.is_branch(target):
        push_branch(target)
    else:
        push_commit(target)


def push_branch(target):
    """Отправить refs,ref указывает на коммит, коммит на файлы"""
    branch_ref = pt.join(CVS_DIR_NAME, REFS_DIR, target)
    send(branch_ref, creation=True)  # отправили адрес
    print(branch_ref)
    print(os.path.getsize(branch_ref))
    send(os.path.getsize(branch_ref))
    with open(branch_ref, 'r') as br:
        commit_name = br.read()
        send(commit_name)
    push_commit(commit_name)


def push_tag(tag):
    """Должен отправлять не файл тега, а тег"""
    tag_file = pt.join(CVS_DIR_NAME, TAG_FILE)
    with open(tag_file, 'r') as tagf:
        tag_list = tagf.readlines()
        try:
            tagging_commit = list(filter(
                lambda x: x.split(' ')[0].find(tag) > -1, tag_list))[0]
            tagging_commit = tagging_commit.split(' ')[1].strip()
        except IndexError as e:
            print(e)
    print('tagging com: ', tagging_commit)
    print(f'{tag} {tagging_commit}')
    send_str(PUSH_TAG_CODE, f'{tag} {tagging_commit}')
    time.sleep(1)
    push_commit(tagging_commit)


def push_commit(commit_name):
    commit_name = pt.join(
                        CVS_DIR_NAME,
                        CVS_DIR_OBJ_NAME,
                        commit_name[:2],
                        commit_name[2:]).strip()
    send(commit_name, creation=True)  # отправили адрес
    print(commit_name)
    print(os.path.getsize(commit_name))
    send(os.path.getsize(commit_name))
    # print("commit_name", commit_name)
    with open(commit_name, 'r') as cm:
        commit_file = ''
        for string in cm:
            commit_file += string
            print("string: ", string)
        send(commit_file)
    with open(commit_name, 'r') as cm:
        files = cm.readlines()
        # print(files)
        for file in files:
            file_path = file.split(" ")[1]
            inner_file = pt.join(
                                CVS_DIR_NAME,
                                CVS_DIR_OBJ_NAME,
                                file_path[:2],
                                file_path[2:]).strip()
            send(inner_file, creation=True)
            print(inner_file)
            print(os.path.getsize(inner_file))
            send(os.path.getsize(inner_file))
            with open(inner_file, 'rb') as inner:
                full_file = b''
                for string in inner:
                    full_file += string
                    print('len', len(full_file))
                send_zip(full_file)


def send(data, creation=False):
    """Отправляем файл на сервер"""
    client_socket = socket.socket()
    client_socket.connect(SERVER_ADDR)
    # print(file)
    data = str(0) + str(int(creation)) + str(data)
    print('sending data:', data)
    client_socket.send(bytes(data, 'UTF-8'))


def send_zip(data):
    client_socket = socket.socket()
    client_socket.connect(SERVER_ADDR)
    data = b'00' + data
    client_socket.send(data)


def send_str(code, string):
    client_socket = socket.socket()
    client_socket.connect(SERVER_ADDR)
    data = code + string
    print('sending data:', data)
    client_socket.send(bytes(data, 'UTF-8'))
