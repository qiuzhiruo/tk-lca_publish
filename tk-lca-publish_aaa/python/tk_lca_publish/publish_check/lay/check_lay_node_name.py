# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import os
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'lay下节点不允许以镜头号命名'
        self.description = u'lay下节点不允许以镜头号命名，否则拆分成ani文件后，会与自动生成的audio节点重名导致一系列错误。\
        \n自动修复会在名字后面加后缀_lay'
        self.auto_fix = True
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:
            shots = pm.ls(type = 'shot')
            seq_shots = [shot.split('_shot')[0] for shot in shots]
            self.existing_shotnames = [str(shotname) for shotname in pm.ls(seq_shots)]
            if self.existing_shotnames:
                msg = '有用镜头号命名的节点存在：\n'
                msg += '\n'.join(self.existing_shotnames)
                return msg
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            for shot_name in self.existing_shotnames:
                pm.rename(shot_name, shot_name + '_lay')
            return ''
        except:
            return traceback.format_exc()

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

