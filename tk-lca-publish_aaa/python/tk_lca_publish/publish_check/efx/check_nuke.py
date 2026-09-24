# coding: utf-8
__author__ = 'john'


import os, glob
import traceback
import re

# All system check classes will use StdCheck as the class name.


def hasNuke(path):
    NUKE_DIR_NAME = 'nuke'

    path = path.rstrip('/')

    if path.endswith('.nuke') and os.path.isfile(path):
        return True

    if path.endswith(NUKE_DIR_NAME) and os.path.isdir(path):
        hasFolder = True
        folder_path = path
    else:
        hasFolder = False
        for currentdir, folders, files in os.walk(path):
            if 'nuke' in folders:
                hasFolder = True
                folder_path = currentdir+'/'+NUKE_DIR_NAME
                break

    if not hasFolder:
        return False

    print folder_path
    nuke_file = glob.glob(folder_path+'/*.nk')
    return len(nuke_file) is not 0


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查预合路径"
        self.description = u"检查是否存在包含nuke文件的名为nuke的文件夹，"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            if self.dialog.w_sys.comboBox_tag.currentIndex() is not 2:
                return ''

            n_cache_items = self.dialog.w_publish_file.listWidget_cache.count()

            has_nuke = False
            for i in range(n_cache_items):
                dir_path = self.dialog.w_publish_file.listWidget_cache.item(i).text()
                if hasNuke(dir_path):
                    has_nuke = True
                break

            if not has_nuke:
                return u'当前模式为预合，但没有检查到nuke'
            return ''

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty
