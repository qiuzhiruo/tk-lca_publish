# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Edward Sun
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

def edo_getPublishDir():
    #Z:\projects\tpr\asset\chr\xiaolai\rig\publish\xiaolai.rig.rigging\anim_rig
    fn=cmds.file(q=1,sn=1)
    pubfn=''
    pubfn=fn.replace('W:/','Z:/').replace('/task/maya/','/publish/').replace('.ma','/')
    return pubfn

def profiling():
    import edo_dgTimerManagerUI.showUi as showUi
    import edo_common
    if cmds.window('edo_dgTimerManagerUI',q=1,ex=1):
        cmds.deleteUI('edo_dgTimerManagerUI')
    mayawindow=edo_common.edo_getMayaWindow()
    ui=showUi.edo_dgTimerManagerUI()
    qtwindow=QtGui.QMainWindow(mayawindow)
    ui.setupUi(qtwindow)
    qtwindow.show()
    output=edo_getPublishDir()
    ui.edo_running_bt_Cmd_(output)
    cmds.deleteUI('edo_dgTimerManagerUI')

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"Profiling Facial Rigging Performance 并写出到publish路径。"
        self.description = u"Profiling Facial Rigging Performance 并写出到publish路径！"
        return

    def proceed(self):
        #print self.dialog.project['name'].upper()
        #self.dialog.anim_file=self.dialog.version_dir+'/anim_rig/'
        #print 'create anim rig.'
        #task=self.dialog.task['name'].lower()
        #finalrigpath=self.dialog.publish_root+'/'+self.dialog.version_name
        #version=finalrigpath.split('.')[-1]
        #finalrigpath=finalrigpath.replace('.'+version,'')
        #finalRigging=finalrigpath.replace(task,'rigging')
        #filename=finalRigging.split('/')[-1].split('.')[0]
        try:
            cmds.playbackOptions(min=1,max=100)
            if cmds.objExists('facial_controls_grp'):
                grp=cmds.group('facial_controls_grp',n='publish_profiling_grp')
                cmds.setKeyframe( grp , t=[1,1], at='ty', v=0 )
                cmds.setKeyframe( grp , t=[100,100], at='ty', v=5 )
                profiling()
                cmds.parent('facial_controls_grp',w=1)
                cmds.delete(grp)
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description