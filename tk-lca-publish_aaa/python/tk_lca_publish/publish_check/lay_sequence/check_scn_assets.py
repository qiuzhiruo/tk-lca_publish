# -*- coding:utf-8 -*-

__author__ = 'xiangquan'

import traceback

import os
import re
import sys
import pymel.core as pm
import maya.cmds as cmds

class StdCheck():
    """
    """
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查|assets|scn下的资产来源"
        self.description = u"检查scn下的assemblyReference是否来自正确的场次"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            seq = os.path.basename(pm.sceneName()).split('.', 1)[0]
            children = cmds.listRelatives('|assets', children = True, fullPath = True)
            result = ''
            illegal_scn_children = []
            if '|assets|scn' in children:
                scn_children = pm.listRelatives('|assets|scn', children = True)
                for scn_child in scn_children:
                    if not scn_child.startswith(seq):
                        illegal_scn_children.append(str(scn_child))
            
            if illegal_scn_children:
                result = u'scn下有节点来源不正确：\n' + '\n'.join(illegal_scn_children)
            return result
        
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


