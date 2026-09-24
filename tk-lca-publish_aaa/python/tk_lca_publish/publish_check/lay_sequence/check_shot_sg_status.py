# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import sys
import os


"""
This check is for sequence rough_layout task only, 
for shot rough_layout task has a sys_check do the same thing
"""

class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查镜头是否允许publish"
        self.description = u"rlo 阶段单个镜头da之后，需要PC将镜头状态改为retake才可以再publish。"
        self.auto_fix = False
        self.duty = u'PC'
        return
    
    def run_check(self):
        try:
            #self.shots_preview_data:  [{'shot_info': {u'sg_cut_in': 121, u'code': u'd40085', ...}]
            illegal_shots = []
            for shot_info in self.dialog.shots_preview_data:
                shot_name = shot_info['shot_info']['code']
                result = self.dialog.sg.find_one('Task', [ ['project', 'name_is', self.dialog.ctx.project['name']],['content', 'is', 'rough_layout'], ['entity','name_is', shot_name]], 
                                                            ['sg_status_list'])
                if result:
                    status = result['sg_status_list']
                    if status == 'da':
                        illegal_shots.append(shot_name)
            
            if illegal_shots:
                msg = u'以下镜头rough_layout任务状态为da，需要PC改为retake才可以继续publish:\n%s' % ('\n'.join(illegal_shots))
                return msg
            
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



