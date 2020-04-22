import socket
import selectors
import os
import os.path as pt
import sys
import time
import types
import errno
import re

# from .. import atomic
# from ..constants import *
# from . import init
# from atomic import add_log
# from constants import *
# socket.gethostname()
ADDR = ('', 1337)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR_NAME = os.path.join(SCRIPT_DIR, '.aw')
CVS_ORIGINAL_DIR_NAME = '.aw'
REPOS_INDEX = 'index'
OBJ_DIR_NAME = 'objects'
HEAD_FILE = 'head'
LOG_FILE = 'log'
TAG_FILE = 'tag'
REFS_DIR = 'refs'
MASTER_REF_FILE = 'master'
# FILE_PATH_CODE = '01'
# PULL_COMMIT_CODE = '10'
# PUSH_TAG_CODE = '02'
# PULL_TAG_CODE = '11'
TMP_FILE = 'tmp.txt'
tmp_file = os.path.join(MAIN_DIR_NAME, TMP_FILE)

parser_regex = re.compile('(?:^save |^push )')

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 1337
HEADER_SIZE = 1024


requests_and_answers = dict()
asking_selector = selectors.DefaultSelector()


def dir_init():

    # В проэкте aw существует отдельный модуль init.py
    # который позволяет инициализировать директорию точно так же
    # при выставленном флаге is_CVS=false
    """ Создает папку .aw в директории, с которой будем работать,
        записываем  """

    os.mkdir(MAIN_DIR_NAME)
    object_dir = pt.join(MAIN_DIR_NAME, OBJ_DIR_NAME)
    os.mkdir(object_dir)
    refs_dir = pt.join(MAIN_DIR_NAME, REFS_DIR)
    os.mkdir(refs_dir)
    master_ref_file = pt.join(MAIN_DIR_NAME, REFS_DIR, MASTER_REF_FILE)
    index_file = pt.join(MAIN_DIR_NAME, REPOS_INDEX)
    tag_file = pt.join(MAIN_DIR_NAME, TAG_FILE)
    open(index_file, 'a').close()
    open(tag_file, 'a').close()
    open(master_ref_file, 'a').close()
    log_file = pt.join(MAIN_DIR_NAME, LOG_FILE)
    open(log_file, 'a').close()
    print('initiated')


def create_listening_socket(host, port):
    """Создаем сокет, слушающий клиента,
    создается один раз!
    """

    # global DEFAULT_PORT
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(50)
    print('server socket listening on', (DEFAULT_HOST, DEFAULT_PORT))
    server_socket.setblocking(False)
    data = types.SimpleNamespace(
        # addr=addr,
        is_server_socket=True)
    asking_selector.register(server_socket, selectors.EVENT_READ, data=data)
    # DEFAULT_PORT += 1


def wrapper_for_accept_connections(server_socket):
    """Принимаем соединение от клиента"""

    conn, addr = server_socket.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(
        addr=addr,
        is_server_socket=False)
    events = selectors.EVENT_READ
    asking_selector.register(conn, events, data=data)


def main():
    dir_init()
    create_listening_socket(DEFAULT_HOST, DEFAULT_PORT)

    while True:
        events = asking_selector.select(timeout=None)
        for key, mask in events:
            if key.data.is_server_socket:
                wrapper_for_accept_connections(key.fileobj)
            else:
                if mask & selectors.EVENT_READ:
                    read_from_socket(key.fileobj)
                # if mask & selectors.EVENT_WRITE:
                #     write_to_socket(key)


def read_from_socket(sock, size=False, file_path=tmp_file):
    """Читаем сообщение. Это может быть запрос(pull, push).
    Это может быть файл.
    нужно разобраться что передано, и отработать в соответствии с сообщением
    """

    if file_path != tmp_file:
        file_path = os.path.join(SCRIPT_DIR, file_path)
        splitted_path = os.path.split(file_path)
        os.makedirs(splitted_path[0], exist_ok=True)
    with open(file_path, mode='wb') as tmp:
        if not size:
            size = HEADER_SIZE
        while True:
            try:
                received_data = sock.recv(size)
                tmp.write(received_data)
                if len(received_data) < size:
                    print('some data received from ', sock.getpeername())
                    break
            except socket.error as exc:
                if exc.errno == errno.WSAECONNRESET:
                    asking_selector.unregister(sock)
                    print('closing connection with:\n', sock.getpeername())
                    sock.close()
                    break
                print('OTHER sockerr:', exc)
    if file_path == tmp_file:
        parse_message(file_path, sock)
    # return incoming_message


def parse_message(tmp_file, socket):
    """Разбор сообщения, перерегистрация сокета с новыми данными
    Может быть строки вида:
    Перед любым сообщением идет его размер
    pull {commit} # регистрируем сокет на запись с номером коммита
    save {file_path} {file_size \\n} {file_content}
    """

    with open(tmp_file, 'r') as tmp:
        first_string = tmp.readline()
        type_of_message = re.search(parser_regex, first_string)[0]
        file_hash = first_string.split()[1]

    if type_of_message == 'pull ':
        data = types.SimpleNamespace(commit_name=file_hash)
        asking_selector.modify(socket,
                               selectors.EVENT_WRITE,
                               data=data)
        send_file(commit_name)
    if type_of_message == 'save ':
        file_size = int(first_string.split()[2])
        file_path = os.path.join(
                        MAIN_DIR_NAME,
                        OBJ_DIR_NAME,
                        file_hash[:2],
                        file_hash[2:]).strip()
        read_from_socket(socket, file_size, file_path)
        # Должен быть переиспользован read_from_socket


def write_to_socket(key):
    """Откуда знаем что писать?
    parse_message должен разобратся, писать или читать, и передать эту информацию дальше
    , например через data в селекторе"""
    pass


def server_init_new():
    create_listening_socket()


main()

# def server_init():
#     server_socket = socket.create_server(
#                                     ADDR,
#                                     family=socket.AF_INET)
#     server_socket.listen(10)
#     print('go!')
#     while(True):
#         conn, address = server_socket.accept()
#         # full_msg = ''
#         full_msg = conn.recv(4096).decode()
#         if full_msg == '':
#             continue
#         print('full_msg ', full_msg)
#         if not full_msg:
#             continue

#         if full_msg[:2] == FILE_PATH_CODE:
#             conn, address = server_socket.accept()
#             file_size = int(conn.recv(4096).decode()[2:])
#             # print(file_size)
#             download_file(full_msg[2:], server_socket, file_size)
#         if full_msg[:2] == PULL_COMMIT_CODE:
#             print('Sending files to client')
#             send_file(full_msg[2:], conn)
#         if full_msg[:2] == PUSH_TAG_CODE:
#             save_tag(full_msg[2:])
#             # conn, address = server_socket.accept()
#             # file_size = int(conn.recv(4096).decode()[2:])


# def save_tag(tag_commit):
#     tag_file = pt.join(MAIN_DIR_NAME, TAG_FILE)
#     # open(tag_file, 'a').close()
#     tag_commit = tag_commit.split(' ')
#     with open(tag_file, 'a') as tag:
#         tag.write(f'{tag_commit[0]} {tag_commit[1]}\n')
#     print('tag saved')


# def send_file(commit_name, socket):
#     """Разбирается что переданно,
#     пересылает файлы"""

#     commit_path = pt.join(
#                         MAIN_DIR_NAME,
#                         OBJ_DIR_NAME,
#                         commit_name[:2],
#                         commit_name[2:]).strip()
#     commit_sending_name = pt.join(
#                         CVS_ORIGINAL_DIR_NAME,
#                         OBJ_DIR_NAME,
#                         commit_name[:2],
#                         commit_name[2:]).strip()
#     send(commit_sending_name, socket, creation=True)  # отправили адрес
#     print('Путь до коммита на сервере', commit_path)
#     # print('commit_sending_name', commit_sending_name)
#     print('Размер файла коммита', os.path.getsize(commit_path))
#     time.sleep(0.4)
#     send(os.path.getsize(commit_path), socket)
#     time.sleep(0.4)
#     # print("commit_name", commit_name)
#     with open(commit_path, 'r') as cm:
#         commit_file = ''
#         for string in cm:
#             commit_file += string
#             print("строка в файле коммита: ", string)
#         print('файл коммита целиком :', commit_file)
#         send(commit_file, socket)
#     with open(commit_path, 'r') as cm:
#         files = cm.readlines()
#         # print(files)
#         for file in files:
#             file_path = file.split(" ")[1]
#             print('хеш файла', file_path)
#             inner_file = pt.join(
#                                 MAIN_DIR_NAME,
#                                 OBJ_DIR_NAME,
#                                 file_path[:2],
#                                 file_path[2:]).strip()
#             inner_file_sending_name = pt.join(
#                                 CVS_ORIGINAL_DIR_NAME,
#                                 OBJ_DIR_NAME,
#                                 file_path[:2],
#                                 file_path[2:]).strip()
#             send(inner_file_sending_name, socket, creation=True)
#             # print('inner_file_sending_name', inner_file_sending_name)
#             print('размер файла', os.path.getsize(inner_file))
#             time.sleep(0.4)
#             send(os.path.getsize(inner_file), socket)
#             time.sleep(0.4)
#             with open(inner_file, 'rb') as inner:
#                 full_file = b''
#                 for string in inner:
#                     full_file += string
#                     # print('len', len(full_file))
#                 print('Полный внутренний файл', full_file)
#                 send_zip(full_file, socket)
#     print('sent!')




#     print("file_path_size", os.path.getsize(file_path))

#     print('end')


# def send(data, socket, creation=False):
#     """Отправляем файл на сервер"""

#     data = str(0) + str(int(creation)) + str(data)
#     socket.send(bytes(data, 'UTF-8'))


# def send_zip(data, socket):
#     # client_socket.connect(SERVER_ADDR)
#     data = b'00' + data
#     socket.send(data)


# # dir_init()
# server_init()


# commit_name = pt.join(
#                     MAIN_DIR_NAME,
#                     OBJ_DIR_NAME,
#                     commit_name[:2],
#                     commit_name[2:]).strip()
# commit_sending_name = pt.join(
#                     CVS_ORIGINAL_DIR_NAME,
#                     OBJ_DIR_NAME,
#                     commit_name[:2],
#                     commit_name[2:]).strip()
#     # send(commit_sending_name, socket, creation=True)  # отправили адрес
# print('commit_name', commit_name)
# print('commit_sending_name', commit_sending_name)
# print(os.path.getsize(commit_name))
#     # send(os.path.getsize(commit_name), socket)
