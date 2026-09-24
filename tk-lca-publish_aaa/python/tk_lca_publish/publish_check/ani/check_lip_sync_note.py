# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.11
#
# Description: As the description shows below
#
############################################

import os
import traceback

IGNORED_LIST = ['z', ]

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查镜头是否通过 Lip Sync 检查。"
        self.description = u"检查镜头有没有内容为 \"Lip Audio Sync Checked\" 的Note。"
        self.auto_fix = False
        self.duty = u"剪辑师和PC。"
        return


    def run_check(self):

        try:
            shot = self.dialog.entity.get('name')
            if any(shot.startswith(i) for i in IGNORED_LIST):
                return ''

            notes = self.dialog.sg.find('Note', [['note_links', 'is', self.dialog.entity], ['content', 'starts_with', 'Lip Audio Sync Checked']], [])
            if len(notes) == 0:
                return u'该镜头还没有通过声音和画面同步的检查，需要找PC协调剪辑师检查发出通过的Note之后才能做 Downstream Publish。'

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


