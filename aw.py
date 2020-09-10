import os
import os.path
import sys
import argparse

import init
import add
import commit
import checkout
import log
import tag
import branch
import reset
import push_pull

functions = {
    "init": init.init,
    "add": add.add,
    "commit": commit.commit,
    "checkout": checkout.checkout,
    "reset": reset.reset,
    "log": log.log,
    "tag": tag.tag,
    "branch": branch.branch,
    "push": push_pull.push,
    "pull": push_pull.pull,
    "register": push_pull.register,
    "hello": push_pull.hello,
}


def main():
    try:
        functions[sys.argv[1]](*sys.argv[2:])
    except KeyError as e:
        print('No such command')


main()
