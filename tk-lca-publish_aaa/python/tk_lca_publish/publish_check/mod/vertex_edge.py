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
        self.check_name = u"角色、群集资产 一个点上最多连5条棱。"
        self.description = u"检查角色。一个点上如果连接的面过多，在subd之后会产生不光滑的渲染效果。一般情况下一个顶点最多连四个面，也就是四条棱，最多不超过5个面。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            if not self.dialog.mod_asset['sg_asset_type'] in ['chr', 'crd']:
                return ""

            if not cmds.objExists('|master|poly|hi'):
                return u'没有找到 |master|poly|hi 组。'

            l_meshes = cmds.listRelatives('|master|poly|hi', ad=True, type='mesh', path=True)
            if not l_meshes:
                return ""

            l_invalid_meshes = []
            l_invalid_vtx = []
            cmds.select(cl=True)

            for mesh_node in l_meshes:
                trans_node = cmds.listRelatives(mesh_node, parent=True, path=True)[0]
                sl = om.MSelectionList()
                sl.add(mesh_node)
                mesh_dag = om.MDagPath()
                sl.getDagPath(0,mesh_dag)

                itMesh = om.MItMeshVertex(mesh_dag)
                vtx_cnt = 0
                edge_cnt = om.MIntArray()
                while not itMesh.isDone():
                    itMesh.getConnectedEdges(edge_cnt)
                    if len(edge_cnt) > 5:
                        l_invalid_meshes.append(mesh_node)
                        l_invalid_vtx.append( trans_node + '.vtx['+str(vtx_cnt)+']')

                    vtx_cnt += 1
                    itMesh.next()

            l_invalid_meshes = list(set(l_invalid_meshes))
            l_invalid_meshes.sort()
            if len(l_invalid_meshes) > 0:
                cmds.select(l_invalid_vtx, r=True)
                return u'有些polygon几何体的顶点连接超过5个面:\n'+', '.join(l_invalid_meshes)

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


