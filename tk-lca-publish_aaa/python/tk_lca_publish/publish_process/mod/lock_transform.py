# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: Yu Hua Zhuo
#
# Date: 2016.12
#
# Description:
#
############################################


import os
import traceback
from xml.dom.minidom import Document
import pymel.core as pm
import maya.cmds as cmds
from proc.function_running_time import record_time

TR_ATTRS=['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ','visibility']
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"锁定模型属性。"
        self.description = u"将模型的属性锁定，防止制作人员误操作。"
        return

    @record_time(__file__)
    def proceed(self):
        try:
            if not cmds.objExists('|master|poly|hi'):
                return u'没有找到 |master|poly|hi 组。'

            l_meshes = cmds.listRelatives('|master|poly|hi', ad=True, type='transform', path=True)
            if not l_meshes:
                return ""


            for mesh in l_meshes:
                pm.lockNode(mesh,lock=0)
                for attr in TR_ATTRS:
                    pm.setAttr(mesh+'.'+attr,l=True)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

