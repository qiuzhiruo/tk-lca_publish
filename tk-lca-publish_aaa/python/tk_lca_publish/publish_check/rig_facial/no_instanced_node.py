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
import maya.cmds as cmds
import maya.mel as mel

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查关联复制的Dag节点。"
        self.description = u"所有组之下不能有关联复制的节点。如果出现，请用自动修复功能转成普通节点。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            grps=['facial_modules_grp', "facial_controls_grp", "facial_skeletons_grp", 'facial_model_grp']
            for grp in grps:
                if not cmds.objExists(grp):
                    return u'没有找到 '+grp+u' 组。'

                l_nodes = cmds.listRelatives(grp, ad=True, fullPath=True)
                for node in l_nodes:
                    l_parents = cmds.listRelatives(node, allParents=True)
                    if len(l_parents) >1:
                        return u"节点: "+ node + u" 是关联复制的物体。"

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''

        try:
            if not cmds.objExists('|master'):
                return u'没有找到 |master 组。'

            l_instanced = []
            l_nodes = cmds.listRelatives('|master', ad=True, fullPath=True)
            for node in l_nodes:
                l_parents = cmds.listRelatives(node, allParents=True, path=True)
                if len(l_parents) >1:
                    l_instanced.extend(l_parents)

            cmds.select(l_instanced, r=True)
            mel.eval('convertInstanceToObject;')
            cmds.select(cl=True)

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


