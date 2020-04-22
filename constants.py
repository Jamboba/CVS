import os.path

MAIN_DIR_NAME = '.aw'
REPOS_INDEX = 'index'
OBJ_DIR_NAME = 'objects'
HEAD_FILE = 'head'
LOG_FILE = 'log'
TAG_FILE = 'tag'
REFS_DIR = 'refs'
MASTER_REF_FILE = 'master'
ROOT_DIR = '.'
TMP_FILE = 'tmp'

head_file = os.path.join(MAIN_DIR_NAME, HEAD_FILE)
tag_file = os.path.join(MAIN_DIR_NAME, TAG_FILE)
log_file = os.path.join(MAIN_DIR_NAME, LOG_FILE)
index_file = os.path.join(MAIN_DIR_NAME, REPOS_INDEX)
master_ref_file = os.path.join(MAIN_DIR_NAME, REFS_DIR, MASTER_REF_FILE)
tmp_file = os.path.join(MAIN_DIR_NAME, TMP_FILE)