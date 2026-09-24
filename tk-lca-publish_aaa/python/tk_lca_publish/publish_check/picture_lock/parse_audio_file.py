# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.08
#
# Description: 
#
########################################################################################

import traceback
import os
import production.audio as audio

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查声音文件是否存在"
        self.description = u"检查声音文件是否存在；获取时长。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            #self.dialog.w_publish_file.tableWidget_shots
            self.dialog.audio_file = self.dialog.w_publish_file.lineEdit_audio.text()
            if not os.path.isfile(self.dialog.audio_file):
                return u"没有找到音频文件: " + self.dialog.audio_file

            if " " in self.dialog.audio_file:
                return u"音频文件路径中有空格: " + self.dialog.audio_file

            self.dialog.audio_length = int(round(audio.getDuration(self.dialog.audio_file)))
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


