# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: Check to see if any vertice are overlapping to each other.
#
########################################################################################

import traceback
import maya.mel as mel
import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"顶点不能重叠(chr,crd,veh)。"
        self.description = u"避免顶点重叠这种情况。如果发生，用自动修复功能可以合并。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            pm.select(cl=True)
            l_invalid = []
            l_invalid_vtx = []

            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']

                if root.fullPath() == '|master':
                    l_meshes = pm.listRelatives('|master|poly', ad=True, type='mesh')
                else:
                    l_meshes = pm.listRelatives(root.name(), ad=True, type='mesh')

                if pm.objExists('|master|shape'):
                    l_meshes.extend(pm.listRelatives('|master|shape', ad=True, type='mesh'))
                    
                if not l_meshes:
                    return ""

                for mesh_node in l_meshes:
                    trans_node = pm.listRelatives(mesh_node, parent=True, path=True)[0]
                    sl = om.MSelectionList()
                    sl.add(mesh_node.name())
                    mesh_dag = sl.getDagPath(0)
                    mesh_mfn = om.MFnMesh(mesh_dag)

                    l_vertice = mesh_mfn.getPoints()
                    d_coordination = {}

                    for i in range(len(l_vertice)):
                        translation_xyz = '%.6f %.6f %.6f' % (l_vertice[i].x, l_vertice[i].y, l_vertice[i].z)
                        if not d_coordination.has_key(translation_xyz):
                            d_coordination[translation_xyz] = 1
                        else:
                            l_invalid.append(mesh_node.name())
                            #d_coordination[translation_xyz] += 1
                            l_invalid_vtx.append(trans_node+'.vtx['+str(i)+']')


            l_invalid = list(set(l_invalid))

            if len(l_invalid) > 0:
                pm.select(l_invalid_vtx)
                return u'有些polygon几何体有重叠的顶点:\n'+', '.join(l_invalid)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''

        try:
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']

                if root.fullPath() == '|master':
                    l_meshes = cmds.listRelatives('|master|poly|hi', ad=True, type='mesh')
                else:
                    l_meshes = cmds.listRelatives(root.name(), ad=True, type='mesh')

                for mesh_node in l_meshes:
                    d_vertice = {}
                    l_invalid = []
                    trans_node = cmds.listRelatives(mesh_node, parent=True, path=True)[0]
                    sl = om.MSelectionList()
                    sl.add(mesh_node)
                    mesh_dag = sl.getDagPath(0)
                    mesh_mfn = om.MFnMesh(mesh_dag)

                    l_vertice = mesh_mfn.getPoints()

                    for i in range(len(l_vertice)):
                        translation_xyz = '%.6f %.6f %.6f' % (l_vertice[i].x, l_vertice[i].y, l_vertice[i].z)
                        if not d_vertice.has_key(translation_xyz):
                            d_vertice[translation_xyz] = []

                        d_vertice[translation_xyz].append(trans_node+'.vtx['+str(i)+']')

                    for k, v in d_vertice.iteritems():
                        if len(v) > 1:
                            l_invalid.extend(v)

                    if len(l_invalid) > 1:
                        cmds.select(l_invalid, r=True)
                        cmds.polyMergeVertex(distance =  0.00001)
                        cmds.select(mesh_node, r=True)
                        mel.eval('DeleteHistory;')
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


