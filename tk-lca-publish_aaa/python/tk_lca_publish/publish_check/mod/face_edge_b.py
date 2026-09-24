# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: Check to see if a face has too many (more than 4) edges.
#
########################################################################################

import traceback
import maya.cmds as cmds
import maya.api.OpenMaya as om
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"所有资产 一个面最多有63条棱。"
        self.description = u"检查角色。一个面上如果棱过多，在subd之后棱的数量有可能会超过255导致渲染报错。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            # if not self.dialog.mod_asset['sg_asset_type'] in ['chr', 'crd']:
            #     return ""

            if not cmds.objExists('|master|poly|hi'):
                return u'没有找到 |master|poly|hi 组。'

            l_meshes = cmds.listRelatives('|master|poly|hi', ad=True, type='mesh', path=True)
            if cmds.objExists('|master|shape'):
                shape_obj=cmds.listRelatives('|master|shape', ad=True, type='mesh', path=True)
                if shape_obj is not None:
                    l_meshes.extend(shape_obj)

            if not l_meshes:
                return ""


            l_invalid_meshes = []
            l_invalid_faces = []

            for mesh_node in l_meshes:
                sl = om.MSelectionList()
                sl.add(mesh_node)
                mesh_dag = sl.getDagPath(0)
                mesh_mfn = om.MFnMesh(mesh_dag)

                for i in range(mesh_mfn.numPolygons):
                    if mesh_mfn.polygonVertexCount(i) > 63:
                        l_invalid_meshes.append(mesh_node)
                        l_invalid_faces.append(mesh_node+'.f['+str(i)+']')

            l_invalid_meshes = list(set(l_invalid_meshes))

            if len(l_invalid_meshes) > 0:
                cmds.select(l_invalid_faces, r=True )
                return u'有些polygon几何体有多于63条棱的面:\n'+', '.join(l_invalid_meshes)

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


