# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Proceed rig publish files
#
############################################

import os
import traceback
import shutil
import pymel.core as pm
import maya.cmds as cmds

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"整理装配文件并拷贝到服务器(含light_loc)。"
        self.description = u"导出文件"
        return

    def proceed(self):

        print('index31 ====================================================================================',self.dialog.tank_file)
        try:
            pm.select("|master", r=True)
            assets=cmds.ls(type='container')
            if assets:
                pm.select(assets,add=True)
            print('index37 ====================================================================================', self.dialog.tank_file)
            pm.exportSelected( self.dialog.tank_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
            pm.exportSelected( self.dialog.tank_file[:-3] + '.mb', force=True, options="v=0;", type="mayaBinary", pr=True, es=True)
            pm.select(cl=True)
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


