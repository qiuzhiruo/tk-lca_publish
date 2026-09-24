# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.09
#
# Description: 
#
########################################################################################

import traceback
import pymel.core as pm
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 concave (两条边的角度大于180) 的面。"
        self.description = u"一般这几种情况会导致面细分错误 。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        self.dialog.mod_asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])

        try:
            l_bad_faces = []

            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']

                if root.fullPath() == '|master':
                    l_meshes = pm.listRelatives('|master|poly|hi', ad=True, type='mesh')
                    if pm.objExists('|master|shape'):
                        l_meshes.extend(pm.listRelatives('|master|shape', ad=True, type='mesh', path=True))
                else:
                    l_meshes = pm.listRelatives(root, ad=True, type='mesh')

                for n in l_meshes:
                    pm.select(n)
                    pm.mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","1","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };')
                    result = pm.ls(sl=1)
                    if result:
                        l_bad_faces.extend(result)

            if len(l_bad_faces)>0:
                pm.select(l_bad_faces, r=True)

                if len(l_bad_faces)<11:
                    l_names = [n.name() for n in l_bad_faces]
                    return "error concave face:" + " ".join(l_names)
                else:
                    l_names = [n.name() for n in l_bad_faces[:10]]
                    return "error concave face:" + " ".join(l_names)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
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


