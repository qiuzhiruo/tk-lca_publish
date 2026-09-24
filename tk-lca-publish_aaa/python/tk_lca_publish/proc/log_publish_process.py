# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import os
import traceback

def log(log_file, content):
    if not os.path.isfile(log_file):
        return

    if not isinstance(content, type('')):
        return

    try:
        fileid = open(log_file, 'r')
        previous = fileid.read()
        fileid.close()
    except:
        print traceback.format_exc()

    try:
        fileid = open(log_file, 'w')
        fileid.write(previous + '\n\n=====================\n'+content)
        fileid.close()
    except:
        print traceback.format_exc()

    return
