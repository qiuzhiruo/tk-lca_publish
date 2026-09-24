# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Copy publish files
#
############################################

import os
import traceback
import shutil


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"清理无效动画曲线"
        self.description = u"清理无效动画曲线。"
        return

    def proceed(self):
        try:
            import pymel.core as pm
            import maya.mel as mel

            l_curves = pm.ls(type="animCurve")
            l_isolated_curves = []
            for c in l_curves:
                if len( pm.listConnections(c , s=False, d=True) ) == 0:
                    if not c.isReferenced():
                        l_isolated_curves.append(c.name())
                        
            if l_isolated_curves:
                pm.lockNode(l_isolated_curves, lock=False)
                pm.general.delete(l_isolated_curves)
            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description


