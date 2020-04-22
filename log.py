# import os
# import os.path

from constants import *


def log(files=None):
    # TODO: список измененных файлов между двумя коммитами
    # log_file = os.path.join(MAIN_DIR_NAME, LOG_FILE)
    with open(log_file, 'r') as log:
        print(log.read())
