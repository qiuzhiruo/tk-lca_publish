# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yingjie
#
#
# Description: 
#
############################################

import os
import traceback
import shutil
from sgtk.platform.qt import QtGui
import maya.cmds as mc
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"修改global_ctrl形状,删除动画节点,隐藏骨骼"
        self.description = u"修改global_ctrl形状,删除动画节点,隐藏骨骼"
        return

    def proceed(self):
        try:
            pos = mc.pointPosition("global_ctrl.cv[5]")[2]
            posa = mc.pointPosition("global_ctrl.cv[4]")[2]
            posb = mc.pointPosition("global_ctrl.cv[6]")[2]

            if (posb - pos)<0 and (posa - pos)<0:
                mc.select('global_ctrlShape.cv[6]','global_ctrlShape.cv[0]','global_ctrlShape.cv[4]','global_ctrlShape.cv[2]',r =1)
                mc.scale(1.5, 1, 1.5, r=1)

            for a in ["animCurveTU","animCurveTL","animCurveTA"]:
                for b in mc.ls(type = a ) or []:
                    if mc.objExists(b):
                        mc.lockNode(b, lock=False)
                        mc.delete(b)

            all_joints = pm.ls(type="joint")
            for joint in all_joints:
                joint.drawStyle.set(2)

            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


