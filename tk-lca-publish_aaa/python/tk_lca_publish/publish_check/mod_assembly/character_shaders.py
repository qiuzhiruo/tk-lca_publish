# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.05
#
# Description: 
#
############################################

import traceback
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"所有资产 需要赋予shader。"
        self.description = u"所有资产 hi 组的所有面都需要付一个 lambert1 之外的shader。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            self.dialog.switch_nodes = None
            l_need_shaders = []
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                l_meshes = pm.listRelatives(root, ad=True, type='mesh')
                for mesh in l_meshes:
                    se = pm.listConnections(mesh.name(), d=True, s=False,  type='shadingEngine')
                    if len(se) == 0 or se[0].name() == 'initialShadingGroup' :
                        l_need_shaders.append(mesh.name())

            if len(l_need_shaders) > 0:
                return u"下列 mesh 需要付 lambert1 之外的材质:\n" + u' '.join(l_need_shaders)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            l_need_shaders = []
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                l_meshes = pm.listRelatives(root, ad=True, type = 'mesh')
                for mesh in l_meshes:
                    se = pm.listConnections(mesh.name(), d=True, s=False,  type='shadingEngine')
                    if len(se) == 0 or se[0].name() == 'initialShadingGroup' :
                        l_need_shaders.append(mesh.name())

            n = pm.createNode('lambert')
            n.setAttr('color', (0.8, 0.8, 0.8))
            pm.select(l_need_shaders, r=True)
            pm.hyperShade(assign = n)
            
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



