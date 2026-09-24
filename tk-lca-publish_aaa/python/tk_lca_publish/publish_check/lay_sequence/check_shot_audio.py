# -*- coding:utf-8 -*-

__author__ = 'xiangquan'

import traceback
import sys
import os

import pymel.core as pm

import lay.lca_camera_sequencer.functions as functions_cs
reload(functions_cs)


# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否每个镜头都有音频文件"
        self.description = u"为了保证每个镜头的时长与音频长度和shotgun长度一致，需要对镜头的audio node进行检查"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            shot_nodes = pm.ls(type = 'shot')
            no_audio_shots = []
            for shot_node in shot_nodes:
                audio_node_inputs = shot_node.attr('audio').inputs()
                if not audio_node_inputs:        # if no audio node appends
                    no_audio_shots.append(str(shot_node))
            
            if no_audio_shots:
                return u'缺少音频文件: \n' + u'\n'.join(no_audio_shots)
            
            return ""
        
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty



