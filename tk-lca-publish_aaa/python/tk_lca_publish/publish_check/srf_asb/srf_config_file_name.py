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

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的Srf Config文件(*.srf)的路径和命名。"
        self.description = u"srf 文件名必须和asb资产名一致"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def check_path(self, path, key):
        p = re.compile("[\w\.]*$")
        tokens = path.replace(":", "\\").replace("/", "\\").split("\\")
        for token in tokens:
            if not p.match(token):
                return key + u" 各级文件夹需要由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成:\n  " + path

        return ''


    def run_check(self):

        try:
            srf_file_path_text = str(self.dialog.w_publish_file.lineEdit_srf.text())
            self.dialog.srf_config_file = srf_file_path_text.split(';')

            for srf_file_path in self.dialog.srf_config_file:
                if srf_file_path == '' or not os.path.isfile(srf_file_path) :
                    return u"找不到这个文件:\n  " + srf_file_path


                file_dir = os.path.dirname(srf_file_path)
                file_name = os.path.basename(srf_file_path)

                result = self.check_path(file_dir, 'Srf config file')
                if result != '':
                    return result

                srf_file_name = self.dialog.entity['name']
                if srf_file_name != file_name.split('.')[0]:
                    return u"srf文件名应该是以资产名开头: "+ srf_file_name

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


