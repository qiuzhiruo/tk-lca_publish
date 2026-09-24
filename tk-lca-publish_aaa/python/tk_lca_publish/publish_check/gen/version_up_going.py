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


from proc.function_running_time import record_time


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查版本(Version)号是否上升和任务是否分配制作者"
        self.description = u"版本名应该是独一无二的，并且版本号应该上升。\n比如之前最高版本为v015，则新版本最低应该是v016。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def mod_srf_check(self,task_group):
        filters = [['entity', 'is', self.dialog.entity], ["content", "is", task_group]]
        sg_tasks = self.dialog.sg.find('Task', filters, ['task_assignees'])
        if not sg_tasks:
            return u'%s\n未找到'+ task_group + u'任务，请联系制片姐姐。' % self.dialog.entity['name']
        for task in sg_tasks:
            assigned_users = task.get('task_assignees')
            if not assigned_users:
                print(task)
                return u"\nshotgun还没有分配"+task_group+u"任务制作者，请告知制片小姐姐。"

        return ""
        
    @record_time(__file__)
    def run_check(self):

        try:
            print(self.dialog.task['name'])

            for v_name in self.dialog.l_old_versions:
                if v_name[:-3] == self.dialog.version_name[:-3] and v_name[-3:].isdigit():
                    if self.dialog.version_num <= v_name[-3:]:
                        return u"之前已经提交了 " + v_name + u", 新版本 " + self.dialog.version_name[-4:] + u" 版本号不够高。请增大版本号。"

            for task_g in ["surfacing"]:
                if self.dialog.task['name'] == task_g:
                    print(self.dialog.task['name'])
                    assignees_check = self.mod_srf_check(task_g)
                    if assignees_check:
                        return assignees_check

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
