import os
import os.path as pt
import sys
import argparse

import add
import commit
import checkout
import log
import tag
import branch
import reset
import push_pull

CVS_DIR_NAME = '.aw'
CVS_REPOS_INDEX = 'index'
CVS_DIR_OBJ_NAME = 'objects'
HEAD_FILE = 'head'
LOG_FILE = 'log'
TAG_FILE = 'tag'
REFS_DIR = 'refs'
MASTER_REF_FILE = 'master'


def init():
    """ Создает папку .aw в директории, с которой будем работать """
    os.mkdir(CVS_DIR_NAME)
    object_dir = pt.join(CVS_DIR_NAME, CVS_DIR_OBJ_NAME)
    os.mkdir(object_dir)
    refs_dir = pt.join(CVS_DIR_NAME, REFS_DIR)
    os.mkdir(refs_dir)
    master_ref = pt.join(CVS_DIR_NAME, REFS_DIR, MASTER_REF_FILE)
    head_file = pt.join(CVS_DIR_NAME, HEAD_FILE)
    index_file = pt.join(CVS_DIR_NAME, CVS_REPOS_INDEX)
    log_file = pt.join(CVS_DIR_NAME, LOG_FILE)
    tag_file = pt.join(CVS_DIR_NAME, TAG_FILE)
    open(index_file, 'a').close()
    with open(head_file, 'w') as headf:
        # print(f'ref: {master_ref}', file=headf)
        headf.write(f'ref: {master_ref}')
    open(log_file, 'a').close()
    open(tag_file, 'a').close()
    open(master_ref, 'a').close()
    print('initiated')


def main():
    # try:
    functions[sys.argv[1]](*sys.argv[2:])
    # except Exception as e:
    #     print(e)


functions = {
    "init": init,
    "add": add.add,
    "commit": commit.commit,
    "checkout": checkout.checkout,
    "reset": reset.reset,
    "log": log.log,
    "tag": tag.tag,
    "branch": branch.branch,
    "push": push_pull.push,
    "pull": push_pull.pull,
}

main()
