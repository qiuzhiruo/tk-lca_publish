# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import os
import sys
import traceback

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查剪辑是否已经取得动画preview"
        self.description = u"动画状态为sc，版本为Downstream，且edt_check状态为ip时，代表剪辑已拿取当前版本的"
        self.auto_fix = False
        self.duty = u"流程管理"
        return

    def run_check(self):
        try:
            #Entity: {'type': 'Shot', 'name': 'm60550', 'id': 10884}
            if self.dialog.entity['type'] == 'Shot':
                shot_name = self.dialog.entity['name']
                edt_check_status = self.dialog.sg.find_one('Task', [['project', 'is', self.dialog.project], ['entity', 'is', self.dialog.entity], 
                                                                    ['content', 'is', 'edt_check']], ['sg_status_list'])
                # if edt_check is not 'ip', pass the check
                if edt_check_status['sg_status_list'] == 'ip':
                    ani_status = self.dialog.sg.find_one('Task', [['project', 'is', self.dialog.project], ['entity', 'is', self.dialog.entity], 
                                                                  ['content', 'is', 'animation']], ['sg_status_list'])
                    vers = self.dialog.sg.find('Version', [ ['project', 'is', self.dialog.project], ['entity','is', self.dialog.entity], ['sg_task', 'name_is', 'animation']], ['code'])
                    ver_names = sorted([ver['code'] for ver in vers])
                    if ver_names:
                        latest_version = ver_names[-1]
                        version_type = self.dialog.sg.find_one('Version', [ ['project', 'is', self.dialog.project], ['entity','is', self.dialog.entity], 
                                                                            ['sg_task', 'name_is', 'animation'], ['code','is', ver_names[-1] ]], ['sg_version_type'])
                    
                    if ani_status['sg_status_list'] in ['sc', 'aa'] and version_type['sg_version_type'] == 'Downstream':
                        return u'edt_check状态为ip, animation状态为sc/aa时，动画不能publish，请联系pc确认镜头状态。'
            
            return ""
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
