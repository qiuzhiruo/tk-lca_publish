# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yu HuaZhuo
#
# Date: 2017.02
#
# Description: Check to mesh points density.
#
########################################################################################

import traceback
import os
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as om
import production.pipeline.lcProdProj as lcp
import re
import sys
from xml.etree import ElementTree
from proc.function_running_time import record_time


# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查模型的点密度。"
        self.description = u"检查模型的点密度，给制作人员参考判断。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            if not cmds.objExists('|master|poly|hi'):
                return u'没有找到 |master|poly|hi 组。'

            l_meshes = pm.listRelatives('|master|poly|hi', ad=True, type='mesh', path=True)
            if not l_meshes:
                return ""

            mesh_p = []
            for hi in l_meshes:

                (hi_min, hi_max) = hi.boundingBox()
                hi_r = hi_max[0] - hi_min[0] + hi_max[1] - hi_min[1] + hi_max[2] - hi_min[2]

                hip = hi.numVertices() / hi_r * 0.00002
                if hip > 1:
                    mesh_p.append(hi)

            if len(mesh_p) > 0:
                pm.select([m.getParent() for m in mesh_p])
                return u'这些模型点数比较多：' + u' ,'.join([m.name() for m in mesh_p])

            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
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
