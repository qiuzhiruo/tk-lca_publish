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
        self.process_name = u"临时处理（人头车）不能提交的问题"
        self.description = u"导出文件"
        return

    def proceed(self):
        try:

            cmds.file(rename=self.dialog.tank_file)
            cmds.file(save=True, type='mayaAscii')

            animPath = self.dialog.tank_file.rsplit("/", 1)
            os.path.join(animPath[0], "anim_rig", animPath[1])

            cmds.file(rename=os.path.join(animPath[0], "anim_rig", animPath[1]))
            cmds.file(save=True, type='mayaAscii')

            cmds.file(rename=os.path.join(animPath[0], "anim_rig", animPath[1])[:-3] + '.mb')
            cmds.file(save=True, type='mayaBinary')





            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


