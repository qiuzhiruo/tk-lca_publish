# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: 
#
########################################################################################

import traceback
import maya.mel as mel
import maya.cmds as cmds
import pymel.core as pm
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
# This module uses maya.cmds because it take less time to parse mesh nodes !
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"漂浮的顶点。"
        self.description = u"有些 poly mesh 上会带着没有和任何面连接的点。这些点会导致后面的publish清理崩溃。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:

            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']

                if root.fullPath() == '|master':
                    l_meshes = pm.listRelatives('|master|poly', ad=True, type='mesh', fullPath=True)
                else:
                    l_meshes = pm.listRelatives(root.name(), ad=True, type='mesh', fullPath=True)

                for mesh in l_meshes:
                    n = pm.listRelatives(mesh, p=True)[0]
                    f = pm.polyEvaluate(n, f=True)
                    v = pm.polyEvaluate(n, v=True)
                    pm.select(n.name() + '.f[0:' + str(f-1) + ']', r=True)
                    mel.eval('PolySelectConvert 3;')
                    v_cnt = pm.polyEvaluate(vc=True)
                    
                    if v_cnt < v:
                        pm.select(n + '.f[0:' + str(f-1) + ']', r=True)
                        mel.eval('PolySelectConvert 3;')
                        pm.select(n + '.vtx[0:' + str(v-1) + ']', tgl=True)
                        return u"Poly mesh " + n + u"有漂浮在面外的点。"
                    
            pm.select(cl=True)
            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty
