# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Guan ZeJie
#
# Date: 2022.08
#
# Description:
#
########################################################################################

import traceback
import pymel.core as pm
from proc.function_running_time import record_time



class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"清除shot和audio类型的脏节点。"
        self.description = u"如果shot和audio类型的脏节点存在, 需要在保存文件之前清理掉。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            shot = pm.ls(type='shot')
            audio = pm.ls(type='audio')
            if shot:
                return u"发现垃圾节点: " + u' '.join([n.name() for n in shot])
            if audio:
                return u"发现垃圾节点: " + u' '.join([n.name() for n in audio])
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            shots = pm.ls(type='shot')
            audios = pm.ls(type='audio')
            lst=shots+audios
            for n in lst:
                pm.lockNode(n.name(),l=0,lu=0)
                pm.delete(n)
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