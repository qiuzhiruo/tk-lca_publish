# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.05
#
# Description: Delete meshes which have no face
#
############################################

import traceback
import os
import pymel.core as pm
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查没有面的mesh。"
        self.description = u"|master|poly下的mesh节点，至少应该有一个面。如果是个空的mesh节点，应该删除。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):

        try:
            l_empty_meshes = []
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']

                l_meshes = pm.listRelatives(root, ad=True, type='mesh')
                for mesh in l_meshes:
                    if mesh.numFaces() == 0:
                        l_empty_meshes.append(mesh.name())

            if len(l_empty_meshes) > 0:
                return u'找到没有面的mesh节点:\n' + '\n'.join(l_empty_meshes)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']

                l_meshes = pm.listRelatives(root, ad=True, type='mesh')
                for mesh in l_meshes:
                    if mesh.numFaces() == 0:
                        p_trans = pm.listRelatives(mesh, p=True)[0]
                        pm.delete(mesh)
                        # Clear parent trans
                        l_nodes = pm.listRelatives(p_trans, c=True, type='mesh')
                        if len(l_nodes) == 0:
                            pm.delete(p_trans)

            return ''

        except:
            return traceback.format_exc()

        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


