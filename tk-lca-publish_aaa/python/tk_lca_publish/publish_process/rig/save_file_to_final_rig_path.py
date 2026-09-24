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
import publish_process.rig.lock_unused_transform as lock_unused_transform

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"如果是成品 : 在合并完成后自动将文件导出到rigging task 的publish路径下。"
        self.description = u"如果是成品 : 在合并完成后自动将文件导出到rigging task 的publish路径下。"
        return

    def proceed(self):
        #print self.dialog.project['name'].upper()
        try:
            tag=self.dialog.version_tag
            #print tag
            if not tag==u"成品":
                return ""
            print u"将文件拷贝到rigging task 的publish路径下"
            task=self.dialog.task['name'].lower()
            finalrigpath=self.dialog.publish_root+'/'+self.dialog.version_name
            version=finalrigpath.split('.')[-1]
            finalrigpath=finalrigpath.replace('.'+version,'')
            finalRigging=finalrigpath.replace(task,'rigging')
            filename=finalRigging.split('/')[-1].split('.')[0]
            finalRigging=finalRigging+'/'+filename+'.ma'
            print finalRigging
            if os.path.exists(finalRigging):
                print 'save and replace ... '+finalRigging
            cmds.file( rename=finalRigging )
            cmds.file( save=True, type='mayaAscii',f=1)
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description