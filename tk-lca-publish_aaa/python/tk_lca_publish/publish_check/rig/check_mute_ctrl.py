# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check asset geometry hierarchy
#
############################################

import traceback
import maya.cmds as cmds
import os
import re
import maya.mel as mel
import maya.cmds as mc


# All system check classes will use StdCheck as the class name.
from assetsystem_sgl.tools.common.publish.ls_nurbsCurve_ctrl import ls_find_mute_ctrl_cmd


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查mute的控制器,pri,sec组"
        self.description = u"检查mute的控制器,pri,sec组"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            wgrps = ls_find_mute_ctrl_cmd()
            wms = ""
            for g in wgrps:
                wms = wms + g + u' : 有mute节点.\n'
            print wms
            return wms

        except:
            return traceback.format_exc()

    def run_fix(self):
        try:
            mc.select(ls_find_mute_ctrl_cmd(), r=True)
            mc.mute(disable=True, force=True)
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
