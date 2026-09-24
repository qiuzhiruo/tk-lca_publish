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
from assetsystem_sgl.tools.common.publish.ls_nurbsCurve_ctrl import ls_findKeyframe_ctrl_cmd


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查有k帧的控制器,pri,sec组"
        self.description = u"检查有k帧的控制器,pri,sec组"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def auto_fix_has_keyframe_controler_cmd(self):
        try:
            mc.select(ls_findKeyframe_ctrl_cmd())
            mel.eval(
                'doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","0","animationList","0","noOptions","0","0" };')
        except:
            pass

    def run_check(self):
        try:
            wgrps = ls_findKeyframe_ctrl_cmd()
            wms = ""
            for g in wgrps:
                wms = wms + g + u' : 有k帧.\n'
            print wms
            return wms

        except:
            return traceback.format_exc()

    def run_fix(self):
        # self.auto_fix_has_keyframe_controler_cmd()
        return

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
