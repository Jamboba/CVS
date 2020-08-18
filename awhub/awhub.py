import socket
import selectors
import os
import os.path as pt
import sys
import time
import types
import errno
import re


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

TMP_FILE = 'tmp.txt'
tmp_file = os.path.join(MAIN_DIR_NAME, TMP_FILE)

parser_regex = re.compile('(?:^save |^load |^stop)')

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 1337
HEADER_SIZE = 49


requests_and_answers = dict()
asking_selector = selectors.DefaultSelector()


def dir_init():
    """ Создает папку .aw в директории, с которой будем работать,
        записываем  """

    if os.path.exists(MAIN_DIR_NAME):
        print('initiated already')
        return
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
    open(tmp_file, 'a').close()
    print('initiated')


def create_listening_socket(host, port):
    """Создаем сокет, слушающий клиента"""

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(50)
    print('server socket listening on', (DEFAULT_HOST, DEFAULT_PORT))
    server_socket.setblocking(False)
    data = types.SimpleNamespace(
        is_server_socket=True)
    asking_selector.register(server_socket, selectors.EVENT_READ, data=data)


def wrapper_for_accept_connections(server_socket):
    """Принимаем соединение от клиента"""

    conn, addr = server_socket.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(
        addr=addr,
        is_server_socket=False,
        socket_file=conn.makefile('rw', newline=''))
    # kek = types.SimpleNamespace()
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
                if read_write(key.data.socket_file):
                    key.fileobj.close()
                    asking_selector.unregister(key.fileobj)
                    continue


def read_write(source_file, size=HEADER_SIZE, destination_file=False):
    """Читаем сообщение. Это может быть запрос(save, load).
    Это может быть файл.
    нужно разобраться что передано, и отработать в соответствии с сообщением
    Должен использоватся и на сервере и на клиенте.
    source/destination - файловый дескриптор
    """

    if not destination_file:
        destination_file = open(tmp_file, mode='w', newline='')
    while True:
        try:
            received_data = source_file.read(size)
            if not received_data:
                continue
            # received_data = received_data.replace('\n\n', '\n')
            print(received_data, file=destination_file, flush=True, end='')
            a = len(received_data)
            if len(received_data) <= size:
                print(bytes(received_data, encoding='utf-8'))
                print('some data received from somewere')
                break
        except Exception as exc:
            print('EXC:', exc)
    try:
        if destination_file.name == tmp_file:
            return parse_message(tmp_file, source_file)
    except AttributeError as e:
        print('Its totally fine')
    # destination_file.close()
    # source_file.close()


def parse_message(tmp_file, socket_file):
    """Разбор сообщения, перерегистрация сокета с новыми данными
    Может быть строки вида:
    # Перед файлом его размер
    load {file_hash} # регистрируем сокет на запись с номером коммита
    save {file_hash} {file_size \\n} {file_content}
    """

    with open(tmp_file, 'r', newline='') as tmp:
        first_string = tmp.readline()
        type_of_message = re.search(parser_regex, first_string)[0]

        if type_of_message == 'stop':
            socket_file.close()
            print('we finished')
            return True

        file_hash = first_string.split()[1]

    if type_of_message == 'load ':
        send_commit(socket_file, file_hash)
        send_header(socket_file, 'stop')
        socket_file.close()
        return True

    if type_of_message == 'save ':
        file_path = get_path_from_hash(file_hash)
        file_size = int(first_string.split()[2])
        splitted_path = os.path.split(file_path)
        os.makedirs(splitted_path[0], exist_ok=True)
        with open(file_path, mode='w', newline='') as destination_file:
            read_write(socket_file, file_size, destination_file)


def send_commit(socket_file, source_hash):
    """Отправить файл индекса, открыть его,
    отправить все файлы, которые лежат внутри"""
    index_path, index_size = get_file_info(source_hash)
    send_header(socket_file, 'load', source_hash, index_size)
    source_fileobj = open(index_path, 'r', newline='')
    read_write(source_fileobj, index_size, socket_file)

    with open(index_path, 'r', newline='') as index:
        for index_line in index:
            _, file_hash = index_line.split(" ")
            file_path, file_size = get_file_info(file_hash)
            send_header(socket_file, 'load', file_hash,  file_size)
            with open(file_path, 'r', newline='') as inner_fileobj:
                read_write(inner_fileobj, file_size, socket_file)


def get_file_info(file_hash):
    file_path = get_path_from_hash(file_hash)
    file_size = os.path.getsize(file_path)
    return file_path, file_size


def send_header(socket_file, command, source_hash=None, file_size=None):
    message_list = [command]
    if source_hash:
        message_list.append(source_hash.strip())
    if file_size:
        message_list.append(str(file_size))
    header_message = ' '.join(message_list)
    print('отправляем заголовок', header_message)
    print(header_message, file=socket_file, flush=True, end='')


def get_path_from_hash(file_hash):
    return os.path.join(
                MAIN_DIR_NAME,
                OBJ_DIR_NAME,
                file_hash[:2],
                file_hash[2:]).strip()


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
