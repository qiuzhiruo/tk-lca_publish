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
import json
import ast

def scale_not_close(scale_values, target=1.0, tol=0.001):
    return any(abs(v - target) > tol for v in scale_values)

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 scale offset"
        self.description = u"检查 scale offset"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        parent1 = cmds.listRelatives('global_ctrl', parent=True)[0]
        parent2 = cmds.listRelatives(parent1, parent=True)[0]
        parent3 = cmds.listRelatives(parent2, parent=True)[0]
        parent4 = cmds.listRelatives(parent3, parent=True)[0]
        parent5 = cmds.listRelatives(parent4, parent=True)[0]
        parent6 = cmds.listRelatives(parent5, parent=True)[0]
        parent7 = cmds.listRelatives(parent6, parent=True)[0]

        parent8 = cmds.listRelatives('root_ctrl', parent=True)[0]
        parent9 = cmds.listRelatives(parent8, parent=True)[0]
        parent10 = cmds.listRelatives(parent9, parent=True)[0]
        parent11 = cmds.listRelatives(parent10, parent=True)[0]
        parent12 = cmds.listRelatives(parent11, parent=True)[0]
        parent13 = cmds.listRelatives(parent12, parent=True)[0]
        parent14 = cmds.listRelatives(parent13, parent=True)[0]

        nodes = [parent1, parent2, parent3, parent4, parent5, parent6, parent7, parent8, parent9, parent10,
            parent11, parent12, parent13,parent14]
        nodeNameList = []
        for node in nodes:
            if node != "root_ctrl":
                nodeNameList.append(str(node))

        scale_list = []

        # Check node scales
        for node in nodeNameList:
            scales = cmds.getAttr('{}.scale'.format(node))[0]  # returns (x, y, z)
            if scale_not_close(scales, 1.0):
                scale_list.append(node)

        # Check root_ctrl
        #if not cmds.objExists('root_ctrl'):
        #    return 'root_ctrl does not exist!'

        root_scales = cmds.getAttr('root_ctrl.scale')[0]

        if scale_not_close(root_scales, 1.0):
            if cmds.objExists('global_ctrl.scale_offset'):
                main_scale = cmds.getAttr('global_ctrl.scale_offset')

                if scale_not_close(root_scales, main_scale):
                    return 'global_ctrl.scale_offset is not equal to root_ctrl.scale'
            else:
                return 'global_ctrl.scale_offset not exist!'

        if scale_list != []:
            return str(scale_list)
        else:
            return ''


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