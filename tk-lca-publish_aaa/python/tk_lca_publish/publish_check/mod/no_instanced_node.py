# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: No instanced nodes
#
########################################################################################

import traceback
import pymel.core as pm
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查关联复制的Dag节点。"
        self.description = u"最高组|master之下不能有关联复制的节点。如果出现，请用自动修复功能转成普通节点。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                l_nodes = pm.listRelatives(root, ad=True, fullPath=True)
                for node in l_nodes:
                    l_parents = pm.listRelatives(node, allParents=True)
                    if len(l_parents) >1:
                        return u"节点: "+ node.name() + u" 是关联复制的物体。"

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''

        try:

            l_instanced = []
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                l_nodes = pm.listRelatives(root, ad=True, fullPath=True, shapes = True)
                for node in l_nodes:
                    l_parents = pm.listRelatives(node, allParents=True)
                    if len(l_parents) >1:
                        l_instanced.extend(l_parents)

            pm.select(l_instanced, r=True)
            pm.mel.eval('convertInstanceToObject;')
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


