# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback

import os
import re
import wave

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的Wav文件(*.wav)采样频率。"
        self.description = u"audio任务下wav文件必须为48000， xiaolai任务下则必须为44100。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            task_name = self.dialog.version_name.split('.')[-2]
            self.dialog.wav_files=[]
            for i in range(self.dialog.w_publish_file.listWidget_wavfiles.count()):
                self.dialog.wav_files.append(str(self.dialog.w_publish_file.listWidget_wavfiles.item(i).text()))

            if len(self.dialog.wav_files) == 0:
                return u"没有提供任何声音文件。请返回重选 wav 文件。"

            for full_wav_file in self.dialog.wav_files:
                wav = wave.open(full_wav_file, 'r')
                wav_frame_rate = wav.getframerate()    
                wav.close()
                if task_name == 'audio':
                    if wav_frame_rate != 48000:
                        return (u'文件采样频率不为48000， 请改正后重新publish: %s' %  os.path.basename(full_wav_file))
                elif task_name == 'xiaolai':
                    if wav_frame_rate != 44100:
                        return (u'文件采样频率不为44100， 请改正后重新publish: %s' %  os.path.basename(full_wav_file))
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


