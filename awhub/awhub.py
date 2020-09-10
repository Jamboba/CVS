import socket
import selectors
import os
import os.path as pt
import sys
import time
import types
import errno
import re
import sqlite3
import hashlib
import shutil

ADDR = ('', 1337)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR_NAME = os.path.join(SCRIPT_DIR, 'users')
CVS_ORIGINAL_DIR_NAME = '.aw'
REPOS_INDEX = 'index'
OBJ_DIR_NAME = 'objects'
HEAD_FILE = 'head'
LOG_FILE = 'log'
TAG_FILE = 'tag'
REFS_DIR = 'refs'
MASTER_REF_FILE = 'master'
DATABASE_NAME = 'users.db'

TMP_FILE = 'tmp.txt'
tmp_file = os.path.join(MAIN_DIR_NAME, TMP_FILE)

parser_regex = re.compile('(?: save| load|^stop|^hello|^register|^auth)')

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 1337
HEADER_SIZE = 100

asking_selector = selectors.DefaultSelector()


def get_database_connection_cursor():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    return (conn, c)


def database_init():
    conn, c = get_database_connection_cursor()
    try:
        c.execute('''CREATE TABLE users(name text, password text,
                                      authentificator text)''')
    except sqlite3.OperationalError as e:
        print(e)
    conn.close()


def check_client(name, password):
    conn, c = get_database_connection_cursor()
    c.execute("SELECT name, password FROM users WHERE name=? AND password=?",
              (name, password))
    result = c.fetchone()
    if result:
        conn.close()
        print(f"hello dear {name}")
        return True
    print(f'no client with such nama and password')
    conn.close()
    return False


def client_dir_init(name):
    users_main_dir = os.path.join(MAIN_DIR_NAME, name)
    if os.path.exists(users_main_dir):
        print('initiated already')
        return
    os.mkdir(users_main_dir)
    users_main_dir = os.path.join(MAIN_DIR_NAME, name, '.aw')
    os.mkdir(users_main_dir)
    object_dir = pt.join(users_main_dir, OBJ_DIR_NAME)
    os.mkdir(object_dir)
    refs_dir = pt.join(users_main_dir, REFS_DIR)
    os.mkdir(refs_dir)
    master_ref_file = pt.join(users_main_dir, REFS_DIR, MASTER_REF_FILE)
    index_file = pt.join(users_main_dir, REPOS_INDEX)
    tag_file = pt.join(users_main_dir, TAG_FILE)
    open(index_file, 'a').close()
    open(tag_file, 'a').close()
    open(master_ref_file, 'a').close()
    log_file = pt.join(users_main_dir, LOG_FILE)
    open(log_file, 'a').close()
    open(tmp_file, 'a').close()
    print('initiated')


def register_client(name, password):
    conn, c = get_database_connection_cursor()
    authentificator = get_auth_key(name, password)
    c.execute("SELECT name FROM users WHERE name=?", (name,))
    if c.fetchone():
        print('this user is already exist')
        return False
    c.execute('INSERT INTO users VALUES (?,?,?)',
              (name, password, authentificator))
    conn.commit()
    print(f'{name} registered successfully')
    conn.close()
    return True


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

    conn, addr = server_socket.accept()
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(
        addr=addr,
        is_server_socket=False,
        socket_file=conn.makefile('rw', newline=''))
    events = selectors.EVENT_READ
    asking_selector.register(conn, events, data=data)


def main():

    if len(sys.argv) == 2 and sys.argv[1] == 'del':
        conn, c = get_database_connection_cursor()
        try:
            c.execute("DROP TABLE users")
        except Exception as e:
            pass
        c.close()
        print('table dropped')
        shutil.rmtree('./users')

    if os.path.exists(MAIN_DIR_NAME):
        print('initiated already')
    else:
        os.mkdir(MAIN_DIR_NAME)

    database_init()

    create_listening_socket(DEFAULT_HOST, DEFAULT_PORT)

    while True:
        events = asking_selector.select(timeout=None, )
        for key, mask in events:
            if key.data.is_server_socket:
                wrapper_for_accept_connections(key.fileobj)
            else:
                if read_write(key.data.socket_file):
                    key.fileobj.close()
                    asking_selector.unregister(key.fileobj)
                    continue


def read_write(source_file, size=HEADER_SIZE, destination_file=False):
    """
    Пишем/читаем из source в destination
    source_file/destination_file - файловый дескриптор
    """

    if not destination_file:
        destination_file = open(tmp_file, mode='w', newline='')
    while True:
        try:
            received_data = source_file.read(size)
            if not received_data:
                continue
            print(received_data, file=destination_file, flush=True, end='')
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


def parse_message(tmp_file, socket_file):
    """Разбор сообщения
    Могут быть строки вида:
    {auth} load {file_hash} # регистрируем сокет на запись с номером коммита
    {auth} save {file_hash} {file_size \\n} {file_content}
    register {name} {password} - регистрация в базе данных
    hello {name} {password} - представится системе для дальнейшей работы
    """

    with open(tmp_file, 'r', newline='') as tmp:
        first_string = tmp.readline()
        type_of_message = re.search(parser_regex, first_string)[0].strip()

    if type_of_message == 'stop':
        socket_file.close()
        print('we finished')
        return True

    if type_of_message == 'register':
        _, name, password = first_string.split()
        if register_client(name, password):
            client_dir_init(name)
        socket_file.close()
        return True

    if type_of_message == 'hello':
        _, name, password = first_string.split()
        if check_client(name, password):
            send_header(socket_file, 'auth', get_auth_key(name, password))
        socket_file.close()
        return True

    if not type_of_message:
        print('Неопознанное сообщение')
        socket_file.close()
        return True

    if type_of_message == 'load':
        auth, _, file_hash = first_string.split()
        send_commit(socket_file, file_hash, auth)
        send_header(socket_file, 'stop')
        socket_file.close()
        return True

    if type_of_message == 'save':
        auth, _, file_hash, file_size = first_string.split()
        file_size = int(file_size)
        client_name = get_client_from_auth(auth)
        if not client_name:
            print("we dont know you")
            return True
        file_path = get_path_from_hash(file_hash, client_name)
        splitted_path = os.path.split(file_path)
        print('путь до файла', file_path)
        os.makedirs(splitted_path[0], exist_ok=True)
        with open(file_path, mode='w', newline='') as destination_file:
            read_write(socket_file, file_size, destination_file)


def send_commit(socket_file, source_hash, auth):
    """Отправить файл индекса, открыть его,
    отправить все файлы, которые лежат внутри"""
    client_name = get_client_from_auth(auth)
    if not client_name:
        print("Back off")
        return
    index_path, index_size = get_file_info(source_hash, client_name)
    send_header(socket_file, 'load', source_hash, index_size)
    source_fileobj = open(index_path, 'r', newline='')
    read_write(source_fileobj, index_size, socket_file)

    with open(index_path, 'r', newline='') as index:
        for index_line in index:
            _, file_hash = index_line.split(" ")
            file_path, file_size = get_file_info(file_hash, client_name)
            send_header(socket_file, 'load', file_hash,  file_size)
            with open(file_path, 'r', newline='') as inner_fileobj:
                read_write(inner_fileobj, file_size, socket_file)


def get_file_info(file_hash, client_name):
    file_path = get_path_from_hash(file_hash, client_name)
    file_size = os.path.getsize(file_path)
    return file_path, file_size


def send_header(socket_file, command, source_hash=None,
                file_size=None, auth=None):
    message_list = [command]
    if source_hash:
        message_list.append(source_hash.strip())
    if file_size:
        message_list.append(str(file_size))
    header_message = ' '.join(message_list)
    header_message = header_message.ljust(HEADER_SIZE, ' ')
    print('отправляем заголовок', header_message)
    print(header_message, file=socket_file, flush=True, end='')


def get_auth_key(name, password):
    """Хэшируем данные для входа"""
    hash = hashlib.blake2b(key=b'randomphrase', digest_size=16)
    hash.update((name+password).encode('utf-8'))
    return hash.hexdigest()


def get_path_from_hash(file_hash, client_name):
    return os.path.join(
                MAIN_DIR_NAME,
                client_name,
                CVS_ORIGINAL_DIR_NAME,
                OBJ_DIR_NAME,
                file_hash[:2],
                file_hash[2:]).strip()


def get_client_from_auth(auth):
    conn, c = get_database_connection_cursor()
    c.execute("SELECT name FROM users WHERE authentificator=?", (auth,))
    client_name = c.fetchone()
    if not client_name:
        print('Who are you?')
        return False
    return client_name[0]


main()
