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
import maya.mel as mel
import maya.OpenMaya as om
import edo_publishListUI.edo_autoCombineFacialRigging_shotgun as edo_autoCombineFacialRigging_shotgun;reload(edo_autoCombineFacialRigging_shotgun)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"如果是成品: 便自动导入body rig 或 facial rig进行combine。"
        self.description = u"如果上传页面第一页选择<模块>，那么仅仅只上传表情或身体rig到数据库，如果选择的是<成品>，那么会自动导入身体设置或表情设置进行合并"
        return

    def proceed(self):
        #print self.dialog.project['name'].upper()
        try:
            tag=self.dialog.version_tag
            #print tag
            tag=self.dialog.version_tag
            #print tag
            if not tag==u"成品":
                return ""
            print u"自动导入合并身体设置和表情设置上传rigging task ..."
            edo_autoCombineFacialRigging_shotgun.edo_combineFcialRigging(0,0)
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
