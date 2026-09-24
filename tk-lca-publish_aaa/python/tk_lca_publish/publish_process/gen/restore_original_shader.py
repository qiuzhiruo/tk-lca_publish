# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Zhang Shirui
#
# Date: 2015.08
#
# Description: Restore the original shaders
#
############################################

import os
import sys
import traceback


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"恢复原有材质"
        self.description = u"恢复工程文件原有材质。"
        return


    def proceed(self):
        try:
            import maya.cmds as cmds

            objs = []



            if not  self.dialog.ori_shading_info:

                print 'not find ori_shading_info'
                return ''

            print 'origin shaders:', self.dialog.ori_shading_info
            print 'new shaders:', self.dialog.new_shaders
            for i in self.dialog.ori_shading_info:
                cmds.sets(self.dialog.ori_shading_info[i], fe = i)

            for i in self.dialog.new_shaders:
                if cmds.sets(i, q=True):
                    objs.extend(cmds.sets(i, q=True))
                shading_grp = cmds.listConnections(i, type='shadingEngine')
                if shading_grp:
                    cmds.delete(shading_grp)
                    
            cmds.sets(objs, fe = 'initialShadingGroup')
            cmds.delete(self.dialog.new_shaders)

            return ''

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


