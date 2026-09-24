# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: pang xuan
#
# Date: 2025.01
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

class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查nodeState"
        self.description = u"检查nodeState"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            constraintNodes = cmds.ls(type='pointConstraint') + cmds.ls(type='orientConstraint') + cmds.ls(type='scaleConstraint') + cmds.ls(type='parentConstraint')
            for each in constraintNodes:
                state = mc.getAttr(each + '.nodeState')
                if state != 0:
                    return each
                if mc.listConnections(each + '.nodeState', s=True):
                    return each
            return ''
        except:
            return ''

    def run_fix(self):
        try:
            constraintNodes = cmds.ls(type='pointConstraint') + cmds.ls(type='orientConstraint') + cmds.ls(type='scaleConstraint') + cmds.ls(type='parentConstraint')
            for each in constraintNodes:
                state = mc.getAttr(each + '.nodeState')
                if state != 0:
                    mc.setAttr(each + '.nodeState', 0)
            return ''
        except:
            return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
