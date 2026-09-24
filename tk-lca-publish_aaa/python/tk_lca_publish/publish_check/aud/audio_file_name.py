# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check shotgun data
#
############################################

import traceback

import os
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        #self.check_name = u"检查提交的Wav文件/Mov文件(*.wav/*.mov)的路径和命名。"
        self.check_name = u"检查提交的Wav文件(*.wav)的路径和命名。"
        #self.description = u"audio任务的Wav/Mov文件必须以镜头号命名，{shot}.wav/{shot}.mov；角色任务则为{shot}_{任务名}.wav"
        self.description = u"audio任务的Wav文件必须以镜头号/场号命名，{shot/seq}.wav；角色任务则为{shot/seq}_{任务名}.wav"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def check_path(self, path, key):
        p = re.compile("[\w\.]*$")
        tokens = path.replace(":", "\\").replace("/", "\\").split("\\")
        for token in tokens:
            if not p.match(token):
                return key + u" 各级文件夹需要由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成:\n  " + path

        return ''


    def run_check(self):
        try:
            task_name = self.dialog.version_name.split('.')[-2]
            self.dialog.wav_files=[]
            for i in range(self.dialog.w_publish_file.listWidget_wavfiles.count()):
                self.dialog.wav_files.append(str(self.dialog.w_publish_file.listWidget_wavfiles.item(i).text()))
            
            #self.dialog.mov_files=[]
            #for i in range(self.dialog.w_publish_file.listWidget_movfiles.count()):
                #self.dialog.mov_files.append(str(self.dialog.w_publish_file.listWidget_movfiles.item(i).text()))
            
            #if len(self.dialog.wav_files) == 0 and len(self.dialog.mov_files) == 0:
                #return u"没有提供任何声音文件或视频文件。请返回重选 wav/mov 文件。"
            
            for f in self.dialog.wav_files:
                f_name = os.path.basename(f)
                if task_name == 'audio':
                    if self.dialog.w_publish_file.seq_checkbox.isChecked():
                        if not f_name.startswith(self.dialog.entity['name']):
                            return (u'文件名称不合格 ，应该是 {场号}.wav 当前为：' + f)
                    else:
                        if not re.search('[a-z][0-9]{5}.wav',f_name) or not f_name.startswith(self.dialog.entity['name']):
                            return (u'文件名称不合格 ，应该是 {镜头号}.wav 当前为：' + f)
                
                elif task_name == self.dialog.task['name']:
                    if self.dialog.w_publish_file.seq_checkbox.isChecked():
                        if not f_name.startswith(self.dialog.entity['name']):
                            return (u'文件名称不合格 ，应该是 {场号}_%s.wav 当前为：' % task_name + f)
                    else:
                        if not re.search('[a-z][0-9]{5}.wav', f_name):
                            if not re.search('[a-z][0-9]{5}_%s.wav' % task_name,f_name) or not f_name.startswith(self.dialog.entity['name']):
                                return ((u'文件名称不合格 ，应该是 {镜头号}_%s.wav 当前为：' % task_name) + f)
            
            #for f in self.dialog.mov_files:
                #f_name = os.path.basename(f)
                #if task_name == 'audio':
                    #if not re.search('[a-z][0-9]{5}.mov',f_name) or not f_name.startswith(self.dialog.entity['name']):
                        #return (u'文件名称不合格 ，应该是 {镜头号}.mov 当前为：' + f)
            
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


