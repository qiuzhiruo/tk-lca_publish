# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.09
#
# Description: 
#
########################################################################################

import traceback
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"如果有UV，必须覆盖所有的面。"
        self.description = u"mesh节点可以没有UV；但如果有UV，所有face都要有UV 。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            self.l_uv_holes = []

            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                l_meshes = pm.listRelatives(root, ad=True, type='mesh')

                for n in l_meshes:
                    f_cnt = pm.polyEvaluate(n, face=True)
                    f_str = '.f[0:%d]' % (f_cnt-1)
                    uv_covered = pm.polyListComponentConversion(n.name()+'.map[*]', fromUV=True, toFace=True)
                    if not (len(uv_covered) == 0 or (uv_covered[0].endswith(f_str))):
                        pm.select(uv_covered, r=True)
                        pm.mel.eval('InvertSelection;')
                        self.l_uv_holes.extend(pm.ls(sl=True))

            if len(self.l_uv_holes) >0:
                pm.select(self.l_uv_holes, r=True)
                return u"没有 uv 的面: \n" + u'\n'.join([str(f) for f in self.l_uv_holes])

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            uv_proj = pm.polyProjection(self.l_uv_holes, ch=1, type='Spherical', ibd=True, sf=True)
            if uv_proj:
                pm.setAttr(uv_proj[0]+ '.rotateX', 45)
                pm.setAttr(uv_proj[0]+ '.rotateY', 45)
                pm.setAttr(uv_proj[0]+ '.rotateZ', 45)

            pm.mel.eval('DeleteAllHistory;')
            pm.select(cl=True)
            return ''
        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


