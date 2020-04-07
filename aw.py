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


def main():
    # try:
    functions[sys.argv[1]](*sys.argv[2:])
    # except Exception as e:
    #     print(e)


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
}

main()
