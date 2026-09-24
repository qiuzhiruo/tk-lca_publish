# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import traceback

import os
import re
import pymel.core as pm

import sys

# All system check classes will use StdCheck as the class name.
class StdCheck():
    """
        dependency: check_hierarchy
    """
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查当前maya文件名是否和task匹配"
        self.description = u"检查当前maya文件名是否和task匹配, 由于flo有final_layout和stereo两个task，为了避免相互混淆而增加此检查"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            # check user name, but only for stereo task
            # if self.dialog.task['name']=='stereo':
            #     return u"没有权限publish stereo task任务"

            current_task = os.path.basename( pm.sceneName() ).split('.')[-3]
            if self.dialog.task['name'] != current_task:
                return u"当前maya文件名与任务名不匹配，请确认是否打开了正确的maya文件。\n" + u"当前maya文件属于 "+current_task+u" 任务， 当前task是 " + self.dialog.task['name']

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



