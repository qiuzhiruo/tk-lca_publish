# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2019 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.07
#
############################################

import traceback
import os
import re
import shutil


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查子资产模型任务"
        self.description = u"检查子资产模型任务是否存在"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            l_no_mod_tasks=[]

            for asset_name, asset in self.dialog.hyperloop.iteritems():
                task = self.dialog.sg.find_one('Task', [['entity', 'is', asset], ['content', 'is', 'model']])
                asset['task'] = task
                if task is None:
                    l_no_mod_tasks.append(asset_name)

            l_no_mod_tasks.sort()
            if len(l_no_mod_tasks) > 0:
                return u"资产没有模型任务：" + ' '.join(l_no_mod_tasks)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            for asset_name, asset in self.dialog.hyperloop.iteritems():
                task = self.dialog.sg.find_one('Task', [['entity', 'is', asset], ['content', 'is', 'model']])
                if task is None:
                    d_task = {'entity': asset,
                              'project': self.dialog.project,
                              'content': 'model',
                              'step': {'type':'Step', 'id':10}
                            }
                    
                    asset['task'] = self.dialog.sg.create('Task', d_task)
            return ''

        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

