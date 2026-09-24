# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check shtogun data
#
############################################

import traceback

import os
import re
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的预览文件的路径和命名。"
        self.description = u"提交的预览文件名由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成，英文字母全小写。\n文件路径所在的各级文件夹命名不能有中文和空格。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        try:
            l_preview_files = [self.dialog.w_file.listWidget_preview.item(i).text() for i in xrange(self.dialog.w_file.listWidget_preview.count())]

            if len(l_preview_files) == 0:
                return u"还没有选择文件。"

            p1 = re.compile("[\w\.-]*$")
            p2 = re.compile("[\w\.]*$")
            for file_path_qtstr in l_preview_files:
                file_path = str(file_path_qtstr)

                if not os.path.isfile(file_path): 
                    return u"找不到这个文件:\n  " + file_path 

                tokens = file_path.replace(":", "\\").replace("/", "\\").split("\\")
                for token in tokens[:-1]:
                    if not p1.match(token):
                        return u"各级文件夹需要由a-z的字母，0-9数字，下划线\"_\"，中划线\"-\"和点\".\"组成:\n  " + "\"" + token + "\" in " + file_path

                if not p2.match(tokens[-1]):
                    return u"文件名需要由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成:\n  " + tokens[-1]

                if tokens[-1] != tokens[-1].lower():
                    return u"\n文件名必须全小写:" + tokens[-1]

                if not '.' in tokens[-1]:
                    return u"\n文件名必须有扩展名:" + tokens[-1]

            self.dialog.l_preview_files = l_preview_files

            return ""

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


