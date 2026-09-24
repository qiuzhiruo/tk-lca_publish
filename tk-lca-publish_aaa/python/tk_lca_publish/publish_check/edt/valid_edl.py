# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.08
#
# Description: 
#
########################################################################################

import os
import traceback


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"为剪辑的 Downstream publish提供了edl文件。"
        self.description = u"为剪辑的 Downstream publish提供了edl文。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            #self.dialog.w_publish_file.tableWidget_shots
            edl_file = str(self.dialog.w_publish_file.lineEdit_edl.text())
            if not os.path.isfile(edl_file):
                return u"没有找到 edl 文件。"

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


