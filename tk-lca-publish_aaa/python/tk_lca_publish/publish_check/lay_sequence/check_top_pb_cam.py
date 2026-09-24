# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import sys
import os

import tank
import pymel.core as pm
import lay.seq_top_playblast.top_pb as top_pb

# All publish process will use StdProcess as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查top_pb_cam相机"
        self.description = u"检查assets|lay下是否存在top_pb_cam相机"
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return
    
    def run_check(self):
        try:
            cam_exist = top_pb.check_top_pb_cam()
            if cam_exist:
                return ""
            else:
                return u"缺少top_pb_cam相机"
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



