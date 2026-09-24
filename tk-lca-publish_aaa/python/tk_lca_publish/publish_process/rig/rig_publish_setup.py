#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/27 11:22
# @File    : rig_publish_setup.py



import os
import traceback
import shutil
import pymel.core as pm
import maya.cmds as mc
import maya.OpenMaya as om

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"解锁rotateOrder"
        self.description = u"解锁rotateOrder"
        return

    def proceed(self):
        try:
            for i in mc.ls("*_ctrl"):
                if mc.nodeType(i) == "joint":
                    if mc.getAttr("{}.rotateOrder".format(i), k=True):
                        if mc.getAttr("{}.rotateOrder".format(i), l=True):
                            mc.setAttr("{}.rotateOrder".format(i), l=False)
                            om.MGlobal.displayInfo("unlock rotateOrder: {}".format(i))
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

