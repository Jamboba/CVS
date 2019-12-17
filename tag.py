import os
import os.path as pt

CVS_DIR_NAME = '.aw'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
CVS_DIR_TEMP = 'tmp'
CVS_IGNORE_FILE = '.awignore.txt'
HEAD_FILE = 'head'
LOG_FILE = 'log'
TAG_FILE = 'tag'

def tag(name=None,commit_hash=None):
    if not name:
        show_tag()
        return
    if not commit_hash:
        head_file = pt.join(CVS_DIR_NAME, HEAD_FILE)
        with open (head_file, 'r') as f:
            ref = f.read().split(' ')[1].strip()
        with open (ref, 'r') as f:
            commit_hash = f.read()
    tag_file = pt.join(CVS_DIR_NAME, TAG_FILE)
    with open(tag_file,'a') as tag:
        print(f'{name} {commit_hash}',file=tag)
    log_file = pt.join(CVS_DIR_NAME, LOG_FILE)
    with open(log_file, 'r') as log:
        log_list = log.readlines()
        tagging_commit = list(filter(lambda x: x.find(commit_hash)>-1,log_list))[0]
        log_list[log_list.index(tagging_commit)] = f'{tagging_commit[:-1]} {TAG_FILE}: {name}\n'
    with open (log_file, 'w') as log:
        for string in log_list:
            log.write(string)
            
def show_tag():
    tag_file = pt.join(CVS_DIR_NAME, TAG_FILE)
    with open(tag_file,'r') as tagf:
        print(tagf.read())