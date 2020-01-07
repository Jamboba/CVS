import socket
import selectors
import os
import os.path as pt
import sys
import time
# socket.gethostname()
ADDR = ('', 1337)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CVS_DIR_NAME = os.path.join(SCRIPT_DIR, '.aw')
CVS_ORIGINAL_DIR_NAME = '.aw'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
HEAD_FILE = 'head'
LOG_FILE = 'log'
TAG_FILE = 'tag'
REFS_DIR = 'refs'
MASTER_REF_FILE = 'master'
FILE_PATH_CODE = '01'
PULL_COMMIT_CODE = '10'
PUSH_TAG_CODE = '02'
PULL_TAG_CODE = '11'


def dir_init():
    """ Создает папку .aw в директории, с которой будем работать,
        записываем  """
    os.mkdir(CVS_DIR_NAME)
    object_dir = pt.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME)
    os.mkdir(object_dir)
    refs_dir = pt.join(CVS_DIR_NAME, REFS_DIR)
    os.mkdir(refs_dir)
    master_ref = pt.join(CVS_DIR_NAME, REFS_DIR, MASTER_REF_FILE)
    index_file = pt.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    tag_file = pt.join(CVS_DIR_NAME, TAG_FILE)
    open(index_file, 'a').close()
    open(tag_file, 'a').close()
    open(master_ref, 'a').close()
    print('initiated')


def server_init():
    server_socket = socket.create_server(
                                    ADDR,
                                    family=socket.AF_INET)
    server_socket.listen(10)
    print('go!')
    while(True):
        conn, address = server_socket.accept()
        # full_msg = ''
        full_msg = conn.recv(4096).decode()
        if full_msg == '':
            continue
        print('full_msg ', full_msg)
        if not full_msg:
            continue

        if full_msg[:2] == FILE_PATH_CODE:
            conn, address = server_socket.accept()
            file_size = int(conn.recv(4096).decode()[2:])
            # print(file_size)
            download_file(full_msg[2:], server_socket, file_size)
        if full_msg[:2] == PULL_COMMIT_CODE:
            print('Sending files to client')
            send_file(full_msg[2:], conn)
        if full_msg[:2] == PUSH_TAG_CODE:
            save_tag(full_msg[2:])
            # conn, address = server_socket.accept()
            # file_size = int(conn.recv(4096).decode()[2:])


def save_tag(tag_commit):
    tag_file = pt.join(CVS_DIR_NAME, TAG_FILE)
    # open(tag_file, 'a').close()
    tag_commit = tag_commit.split(' ')
    with open(tag_file, 'a') as tag:
        tag.write(f'{tag_commit[0]} {tag_commit[1]}\n')
    print('tag saved')


def send_file(commit_name, socket):
    """Разбирается что переданно,
    пересылает файлы"""
    commit_path = pt.join(
                        CVS_DIR_NAME,
                        CVS_DIR_OBJ_NAME,
                        commit_name[:2],
                        commit_name[2:]).strip()
    commit_sending_name = pt.join(
                        CVS_ORIGINAL_DIR_NAME,
                        CVS_DIR_OBJ_NAME,
                        commit_name[:2],
                        commit_name[2:]).strip()
    send(commit_sending_name, socket, creation=True)  # отправили адрес
    print('Путь до коммита на сервере', commit_path)
    # print('commit_sending_name', commit_sending_name)
    print('Размер файла коммита', os.path.getsize(commit_path))
    time.sleep(0.4)
    send(os.path.getsize(commit_path), socket)
    time.sleep(0.4)
    # print("commit_name", commit_name)
    with open(commit_path, 'r') as cm:
        commit_file = ''
        for string in cm:
            commit_file += string
            print("строка в файле коммита: ", string)
        print('файл коммита целиком :', commit_file)
        send(commit_file, socket)
    with open(commit_path, 'r') as cm:
        files = cm.readlines()
        # print(files)
        for file in files:
            file_path = file.split(" ")[1]
            print('хеш файла', file_path)
            inner_file = pt.join(
                                CVS_DIR_NAME,
                                CVS_DIR_OBJ_NAME,
                                file_path[:2],
                                file_path[2:]).strip()
            inner_file_sending_name = pt.join(
                                CVS_ORIGINAL_DIR_NAME,
                                CVS_DIR_OBJ_NAME,
                                file_path[:2],
                                file_path[2:]).strip()
            send(inner_file_sending_name, socket, creation=True)
            # print('inner_file_sending_name', inner_file_sending_name)
            print('размер файла', os.path.getsize(inner_file))
            time.sleep(0.4)
            send(os.path.getsize(inner_file), socket)
            time.sleep(0.4)
            with open(inner_file, 'rb') as inner:
                full_file = b''
                for string in inner:
                    full_file += string
                    # print('len', len(full_file))
                print('Полный внутренний файл', full_file)
                send_zip(full_file, socket)
    print('sent!')


def download_file(file_path, socket, size):
    file_path = pt.join(SCRIPT_DIR, file_path)
    splitted_path = os.path.split(file_path)
    # print("file_path", splitted_path)
    os.makedirs(splitted_path[0], exist_ok=True)
    print('file_path', file_path)
    with open(file_path, 'wb') as file:
        conn, address = socket.accept()
        print(size+2)
        data = conn.recv(size+2)[2:]
        # len
        file.write(data)
    
    print("file_path_size", os.path.getsize(file_path))

    print('end')


def send(data, socket, creation=False):
    """Отправляем файл на сервер"""
    # client_socket = socket.socket()
    # client_socket.connect(SERVER_ADDR)
    # print(file)
    data = str(0) + str(int(creation)) + str(data)
    # print(data, 'UTF-8')
    socket.send(bytes(data, 'UTF-8'))


def send_zip(data, socket):
    # client_socket.connect(SERVER_ADDR)
    data = b'00' + data
    socket.send(data)


# dir_init()
server_init()


# commit_name = pt.join(
#                     CVS_DIR_NAME,
#                     CVS_DIR_OBJ_NAME,
#                     commit_name[:2],
#                     commit_name[2:]).strip()
# commit_sending_name = pt.join(
#                     CVS_ORIGINAL_DIR_NAME,
#                     CVS_DIR_OBJ_NAME,
#                     commit_name[:2],
#                     commit_name[2:]).strip()
#     # send(commit_sending_name, socket, creation=True)  # отправили адрес
# print('commit_name', commit_name)
# print('commit_sending_name', commit_sending_name)
# print(os.path.getsize(commit_name))
#     # send(os.path.getsize(commit_name), socket)
