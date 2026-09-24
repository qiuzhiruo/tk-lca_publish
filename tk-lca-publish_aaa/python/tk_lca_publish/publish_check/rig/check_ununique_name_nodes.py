# -*- coding:utf-8 -*-
import traceback
import maya.cmds as cmds
import os
import re
from assetsystem_sgl.tools.common.publish.ls_ununique_name_nodes import ls_ununique_name_nodes_cmd, auto_fix_transform_name_cmd
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查重名节点'
        self.description = u'检查重名节点'
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            ununique_name_nodes = ls_ununique_name_nodes_cmd()
            if ununique_name_nodes:
                msg = u' 场景中有重名节点\n'+"\n".join(ununique_name_nodes)
                return msg

            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix gentest'''
        try:
            auto_fix_transform_name_cmd()
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

