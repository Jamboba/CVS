import socket
import os
import os.path
import sys
import time
import checkout
import re

import atomic
from constants import *

SERVER_ADDR = ('localhost', 1337)
HEADER_SIZE = 49
parser_regex = re.compile('(?:^save |^load |^stop)')


def pull(commit_name):
    """ Скачивает коммит с сервера """
    client_socket_file = open_connection()
    send_header(client_socket_file, 'load', commit_name)
    while True:
        if read_write(client_socket_file):
            client_socket_file.close()
            break
    # client_socket_file.close()


def push(commit_name):
    """ Закачивает коммит на сервер"""
    client_socket_file = open_connection()
    send_commit(client_socket_file, commit_name)
    send_header(client_socket_file, 'stop')
    client_socket_file.close()


def open_connection():
    client_socket = socket.socket()
    client_socket.connect(SERVER_ADDR)
    # client_socket.settimeout(2)
    client_socket_file = client_socket.makefile('rw', newline='')
    return client_socket_file


def read_write(source_file, size=HEADER_SIZE, destination_file=False):
    """Читаем/отправляем сообщение. Это запрос(save, load).
    нужно разобраться что передано, и отработать в соответствии с сообщением
    Должен использоватся и на сервере и на клиенте.
    source/destination - файловый дескриптор
    """

    if not destination_file:
        destination_file = open(tmp_file, mode='w', newline='')
    # print(destination_file, type(destination_file))
    while True:
        try:
            received_data = source_file.read(size)
            # Если за раз переданно не все сообщение?
            if not received_data:
                # временное решение
                continue
            # received_data = received_data.replace('\n\n', '\n')
            print(received_data, file=destination_file, flush=True, end='')
            if len(received_data) <= size:
                print(bytes(received_data, encoding='utf-8'))
                print('длинна', len(received_data))
                print('some data tranfered from/to somewere')
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
    """Разбор сообщения
    Может быть строки вида:
    # Перед файлом его размер
    save {file_hash} # регистрируем сокет на запись с номером коммита
    load {file_hash} {file_size \\n}( {file_content} - следующим сообщением)
    """
    with open(tmp_file, 'r', newline='') as tmp:
        first_string = tmp.readline()
        type_of_message = re.search(parser_regex, first_string)[0]

        if type_of_message == 'stop':
            socket_file.close()
            print('we finished')
            return True

        file_hash = first_string.split()[1]

    if type_of_message == 'save ':
        send_commit(socket_file, file_hash)

    if type_of_message == 'load ':
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
    send_header(socket_file, 'save', source_hash, index_size)
    source_fileobj = open(index_path, 'r', newline='')
    read_write(source_fileobj, index_size, socket_file)

    with open(index_path, 'r', newline='') as index:
        for index_line in index:
            _, file_hash = index_line.split(" ")
            file_path, file_size = get_file_info(file_hash)
            send_header(socket_file, 'save', file_hash, file_size)
            with open(file_path, 'r', newline='') as inner_fileobj:
                read_write(inner_fileobj, file_size, socket_file)


def get_file_info(file_hash):
    file_path = get_path_from_hash(file_hash)
    file_size = os.path.getsize(file_path)
    print(file_path, 'size', file_size)
    print('another size', os.stat(file_path).st_size)
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
