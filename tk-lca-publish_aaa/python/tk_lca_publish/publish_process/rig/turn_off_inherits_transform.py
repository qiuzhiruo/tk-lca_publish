# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.05
#
# Description: 
#
############################################

import os
import traceback
import shutil
import pymel.core as pm
from sgtk.platform.qt import QtGui
import maya.cmds as cmds

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"关闭部分组的继承位移。"
        self.description = u"关闭poly ，shape ,  anim_skeletons_grp  ,  anim_modules_grp  ,  tech_skeletons_grp  ,  tech_modules_grp 的继承位移。"
        return


    def proceed(self):
        try:
            grps=['|master|poly','|master|shape','|master|rig|anim_rig|anim_skeletons_grp','|master|rig|anim_rig|anim_modules_grp','|master|rig|tech_rig|tech_skeletons_grp','|master|rig|tech_rig|tech_modules_grp']
            for grp in grps:
                if cmds.objExists(grp):
                    try:
                        cmds.setAttr(grp+'.inheritsTransform',False)
                    except:
                        None
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description