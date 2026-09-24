# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import os

import gene.shot_owner_funcs.functions as funcs_sof
reload(funcs_sof)

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查任务(Task)的是否有权限publish。"
        self.description = u"检查镜头的sg_task_owner属性，看是否为当前任务。"
        self.auto_fix = False
        self.duty = u"流程管理"
        return


    def run_check(self):

        try:
            show_owner = funcs_sof.Funcs()
            #e.g. crnt_shot_owner ={'id': 8833, 'sg_shot_owner': None, 'type': 'Shot'} or
            # crnt_shot_owner = {'id': 8833, 'sg_shot_owner': {'id': 130686, 'name': 'final_layout', 'type': 'Task'}, 'type': 'Shot'}
            crnt_shot_owner = show_owner.get_crnt_shot_owner_info()
            sg_shot_owner = crnt_shot_owner['sg_shot_owner']
            if sg_shot_owner is not None:
                if show_owner.task_name != sg_shot_owner['name']:
                    return u'没有publish权限，当前镜头权限属于 ' + sg_shot_owner['name']
            return ''
        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        return ""


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

