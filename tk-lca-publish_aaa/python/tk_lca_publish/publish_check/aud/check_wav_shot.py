# -*- coding:utf-8 -*-

__author__ = 'xiangquan'

import traceback

import os
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的Wav文件(*.wav)对应的镜头号在shotgun上是否存在。"
        self.description = u"wav对应的镜头必须存在才能顺利publish"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            if self.dialog.w_publish_file.seq_checkbox.isChecked():     # sequence mode
                return ''
            else:           # shot mode
                wav_shots = []
                for i in range(self.dialog.w_publish_file.listWidget_wavfiles.count()):
                    wav_file = os.path.basename(str(self.dialog.w_publish_file.listWidget_wavfiles.item(i).text()))
                    wav_shot = os.path.splitext(wav_file)[0]
                    wav_shots.append(wav_shot.split('_')[0])
                
                if not wav_shots:
                    return u"没有提供任何声音文件。请返回重选 wav 文件。"
                
                shot_data = self.dialog.sg.find('Sequence', [ ['project', 'name_is',self.dialog.project['name']], 
                                                              ['code', 'is', self.dialog.entity['name']] ], ['shots'])[0]['shots']
                sg_shots = [shot_dict['name'] for shot_dict in shot_data]
                
                illegal_shots = []
                for wav_shot in wav_shots:
                    if wav_shot not in sg_shots:
                        illegal_shots.append(wav_shot)
                        
                if illegal_shots:
                    msg = u'\n'.join(illegal_shots)
                    return u'Shotgun上缺少这些音频对应的镜头号：\n' + msg
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


