# -*- coding:utf-8 -*-

__author__ = 'xiangquan'

import traceback

import os
import re
import sys
import pymel.core as pm
import maya.cmds as cmds

ROOT_HIERARCHY = '|assets|lay'
LEGAL_GROUPS = ['temp_assets', 'VFX']
CAM_RIG_CURVE = 'cam_rig:global_ctrl'

class StdCheck():
    """
    """
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查polygon是否在正确的层级"
        self.description = u"艺术家自建的polygon在publish时都需要在 assets|lay下的temp_assets 或 VFX组里，不能直接散放在assets|lay下面"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            meshes = cmds.listRelatives(ROOT_HIERARCHY, allDescendents = True, type = 'mesh', fullPath = True)
            lay_children = pm.listRelatives(ROOT_HIERARCHY, children = True)
            LEGAL_GROUPS = []
            for lay_child in lay_children:
                all_trans = set(pm.listRelatives(lay_child, children = True, type = 'transform'))
                all_children = set(pm.listRelatives(lay_child, children = True))
                if not all_trans ^ all_children:       # if all children are transform, then the lay_child node is a group node, which is a legal hierarchy for polygon.
                    LEGAL_GROUPS.append(str(lay_child))
            LEGAL_GROUPS = list(set(LEGAL_GROUPS))
            
            illegal_meshes = []
            for mesh in meshes:
                short_mesh = mesh.replace(ROOT_HIERARCHY + '|', '')
                legal_mesh = False
                for group_name in LEGAL_GROUPS:
                    if group_name in short_mesh:
                        legal_mesh = True
                        break
                
                if not legal_mesh:
                    node = short_mesh.split('|', 1)[0]
                    if node.endswith(CAM_RIG_CURVE):
                        legal_mesh = True
                    else:
                        children = cmds.listRelatives(node, children = True, type = 'nurbsCurve')
                        if children:
                            legal_mesh = True
                
                if not legal_mesh:
                    illegal_meshes.append(mesh)
            
            result = ''
            if illegal_meshes:
                result = u'|assets|lay下有polygon存在：\n' + '\n'.join(illegal_meshes)
            return result
        
        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


