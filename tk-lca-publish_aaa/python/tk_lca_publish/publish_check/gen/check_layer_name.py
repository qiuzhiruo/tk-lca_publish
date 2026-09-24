# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import traceback

import os
import re
import pymel.core as pm
import sys

# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 Displayer Layer 命名。"
        self.description = u"镜头中的 displayer layer 命名应该有含义，不能是缺省的 layer1, layer2 这种。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            l_layers = pm.ls(type = 'displayLayer')
            l_to_fix = []
            for layer in l_layers:
                layer_name = layer.name()
                if layer_name.startswith('layer'):
                    if layer_name[5:].isdigit():
                        l_to_fix.append(layer_name)

            if len(l_to_fix) > 0:
                return u"以下 Displayer Layer 需要调整命名:\n    " + ' '.join(l_to_fix)

            return ""

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



