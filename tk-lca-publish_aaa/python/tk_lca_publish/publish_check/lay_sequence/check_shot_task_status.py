# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import pprint
import os

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查任务(Task)和任务所属的资产/镜头是否已经da/final。"
        self.description = u"Shotgun上如果任务的状态变为da/fin/omt就不能再publish了。如果一定要publish，需要找到项目管理修改任务状态。"
        self.auto_fix = False
        self.duty = u"项目管理。"
        return


    def run_check(self):

        try:
            error_shots = []
            for data in self.dialog.shots_preview_data:
                shot_name = data['shot_info']['code']
                shot_task_info = self.dialog.sg.find_one('Task', [['project', 'name_is', self.dialog.project['name']], 
                                                           ['entity', 'name_is', shot_name], ['content', 'is', 'rough_layout']], ['sg_status_list'])
                if not shot_task_info['sg_status_list']:
                    error_shots.append(shot_name)
    
                if shot_task_info['sg_status_list'] in ['omt', 'fin', 'da']:
                    error_shots.append(shot_name)
    
                shot_info = self.dialog.sg.find_one('Shot', [['project', 'name_is', self.dialog.project['name']],['code', 'is', shot_name]], 
                                                    ['sg_status_list'])
                if not shot_info['sg_status_list']:
                    error_shots.append(shot_name)
    
                if shot_info['sg_status_list'] in ['omt', 'fin']:
                    error_shots.append(shot_name)
            
            msg = ''
            if error_shots:
                msg += u'以下镜头任务或镜头状态不允许publish，请找pc检查任务状态:\n'
                msg += '\n'.join(error_shots)
                msg += '\n'
            return msg

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

