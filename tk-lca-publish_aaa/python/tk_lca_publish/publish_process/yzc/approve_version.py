# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.12
#
# Description: 
#
############################################

import os
import sys
import traceback
from production.shotgun_utils.sg_updater import Updater


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将满足条件的版态设为 apr/通过, 并将任务设为 sc"
        self.description = u"将满足条件的版态设为 apr/通过, 并将任务设为 sc"
        self.updater = Updater(self.dialog.sg)
        return

    def do_approve(self, reason=u"新 Publish 了（自动认为艺术通过的）Downstream 版本"):
        self.dialog.sg.update('Version', self.dialog.v_info['id'], {'sg_status_list': 'apr'} )
        self.updater.update_task_status(self.dialog.task, 'sc', reason)
        return

    def has_aa_mark(self):
        task_info = self.dialog.sg.find_one('Task', [['id', 'is', self.dialog.task['id']]], ['sg_status_list'])
        if task_info['sg_status_list'] in ['aaa', 'aa']:
            return True

        l_versions = self.dialog.sg.find('Version', [['sg_task', 'is', self.dialog.task], ['sg_status_list', 'is', 'apr']])
        if len(l_versions) > 0:
            return True
        else:
            return False

    def has_aa_mark_mod(self):
        task_info = self.dialog.sg.find_one('Task', [['id', 'is', self.dialog.task['id']]], ['sg_status_list'])
        if task_info['sg_status_list'] in ['aa']:
            return True

        l_versions = self.dialog.sg.find('Version', [['sg_task', 'is', self.dialog.task], ['sg_status_list', 'is', 'apr']])
        if len(l_versions) > 0:
            return True
        else:
            return False

    def proceed(self):
        try:
            if self.dialog.version_tag == u"测试":
                return ""

            if self.dialog.step['id'] == 10 and self.dialog.task['name'] == 'model':
                if self.has_aa_mark_mod() and self.dialog.version_tag == u"精模":
                    self.do_approve(reason=u"model 任务之前有艺术通过的版本，现在新 PA 了 donwstream 版本")
            elif self.dialog.step['id'] == 12 and self.dialog.task['name'] == 'surfacing':
                if self.has_aa_mark():
                    self.do_approve(reason=u"surfacing 任务之前有艺术通过的版本，现在新 PA 了 donwstream 版本")
            elif self.dialog.step['id'] == 58:
                if self.dialog.task['name'] == 'hair':
                    if self.has_aa_mark():
                        self.do_approve(reason=u"hair 任务之前有艺术通过的版本，现在新 PA 了 donwstream 版本")
                elif self.dialog.task['name'] == 'cloth':
                    self.do_approve()
            elif self.dialog.step['id'] == 57:
                if self.dialog.task['name'] == 'hair':
                    if self.has_aa_mark():
                        self.do_approve(reason=u"hair 任务之前有艺术通过的版本，现在新 PA 了 donwstream 版本")
                elif self.dialog.task['name'] == 'cloth':
                    self.do_approve()
            elif self.dialog.step['id'] == 5:
                if  self.dialog.task['name'] == 'animation':
                    if self.has_aa_mark():
                        self.do_approve(reason=u"animation 任务之前有艺术通过的版本，现在新 PA 了 donwstream 版本")
            elif self.dialog.step['id'] == 91:
                if self.has_aa_mark():
                    self.do_approve(reason=u"plt 任务之前有艺术通过的版本，现在新 PA 了 donwstream 版本")
            elif self.dialog.step['id'] == 11:
                if self.dialog.version_tag == u"完整版":
                    self.do_approve()
            else:
                self.do_approve()

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


