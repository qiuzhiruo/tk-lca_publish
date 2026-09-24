# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: Check to see if too many (more than 5) faces are connected on a vertex.
#
########################################################################################

import traceback
import maya.cmds as cmds
import maya.OpenMaya as om
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"角色、群集资产 身体拓扑的边长最短0.002。"
        self.description = u"检查角色、群集资产身体拓扑的边的长度不能小于0.002，否则会刷不上权重。使用自动修复会把边延长到0.003。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:

            
            if self.dialog.project['name'].upper() == 'CAT':
                return ""

            if not self.dialog.mod_asset['sg_asset_type'] in ['chr', 'crd']:
                return ""

            self.l_invalid_meshes_edges=[]
            skin_grp='|master|poly|hi|mesh_grp|skin*'

            if not cmds.objExists(skin_grp):
                return u'没有找到 |master|poly|hi|mesh_grp|skin_grp 组。'

            l_meshes = cmds.listRelatives(skin_grp, ad=True, type='mesh', path=True)
            if not l_meshes:
                return ""

            cmds.select(cl=True)

            edges = cmds.polyListComponentConversion(l_meshes, te = True)
            cmds.select(edges)
            cmds.polySelectConstraint(m = 3, type = 0x8000, l = 1, lb = [0.0, 0.002])
            l_invalid_meshes_edges = cmds.ls(sl = True)
            l_invalid_meshes=list(set([m.split('.')[0] for m in l_invalid_meshes_edges]))
            if 0 < len(l_invalid_meshes) :
                self.l_invalid_meshes_edges=l_invalid_meshes_edges
                return u'已经选中边的长度小于0.002的mesh:\n'+', '.join(l_invalid_meshes)
            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            import math

            for e in self.l_invalid_meshes_edges:
                object = e.split('.')[0]
                points = cmds.polyListComponentConversion(e, fe = True, tv = True)
                p1 = cmds.listAttr(points)[0]
                p2 = cmds.listAttr(points)[4]
                p1_pos = cmds.pointPosition(str(object)+'.'+str(p1))
                p2_pos = cmds.pointPosition(str(object)+'.'+str(p2))
                edge_length = math.sqrt((p1_pos[0]-p2_pos[0])**2+(p1_pos[1]-p2_pos[1])**2+(p1_pos[2]-p2_pos[2])**2)
                scaler = 0.003/edge_length
                cmds.scale(scaler, scaler, scaler, e, xyz = True, pivot=p1_pos, r = True)

        except:
            return traceback.format_exc()


        return ''

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


