import os
import os.path
from shutil import copyfile

from constants import *
from atomic import hash_obj, add_log, write_ref


def commit(tag=None):
    index_path = os.path.join(MAIN_DIR_NAME, REPOS_INDEX)
    commit_hash = hash_obj(index_path)
    commit_dir_path = os.path.join(
            MAIN_DIR_NAME,
            OBJ_DIR_NAME,
            commit_hash[0:2]
            )
    try:
        os.mkdir(commit_dir_path)
    except FileExistsError as e:
        print(e)
        return
    commit_file_path = os.path.join(commit_dir_path, commit_hash[2:])
    copyfile(index_path, commit_file_path)
    write_ref(commit_hash)
    add_log(commit_hash)
