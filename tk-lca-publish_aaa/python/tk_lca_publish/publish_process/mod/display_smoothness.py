# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.06
#
# Description: 
#
############################################

import os
import traceback
from proc.function_running_time import record_time

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"模型按1显示。"
        self.description = u"将模型的 display smoothness 精度降低，提高下游制作速度。"
        return

    @record_time(__file__)
    def proceed(self):
        try:
            import pymel.core as pm
            l_meshes = pm.ls( type='mesh')
            for mesh in l_meshes:
                pm.displaySmoothness(mesh, polygonObject=0)
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


