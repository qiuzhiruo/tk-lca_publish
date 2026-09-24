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
import shutil

def edo_getPublishDir():
    #Z:\projects\tpr\asset\chr\xiaolai\rig\publish\xiaolai.rig.rigging\anim_rig
    fn=cmds.file(q=1,sn=1)
    pubfn=''
    pubfn=fn.replace('W:/','Z:/').replace('/task/maya/','/publish/').replace('.ma','/')
    return pubfn

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将body rig sys 的profiling data 拷贝到数据库。"
        self.description = u"将body rig sys 的profiling data 拷贝到数据库！"
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
            output=edo_getPublishDir()
            if os.path.exists(output):
                if cmds.objExists('master.body_sys_profiling_data'):
                    data=cmds.getAttr('master.body_sys_profiling_data')
                    if data==None:
                        return ""
                    if os.path.exists(data):
                        #output='D:/'
                        print 'copy ... '+data+' ...to... '+output+'/profilingData.txt'
                        shutil.copy(data,output+'/profilingData.txt')
                        #help(shutil)

            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description