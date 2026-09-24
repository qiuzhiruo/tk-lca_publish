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
import pymel.core as pm
from proc.function_running_time import record_time


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"资产 一个面最多有4条棱"
        self.description = u"一个面上如果棱过多，在subd之后会产生不光滑的渲染效果。如果面有四条以上的棱，应该切成更小的面.(skip tag: face_edge）"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def check_all_skin_group(self,grp_skin):

        skin_get_children = grp_skin.getChildren()

        for grp in skin_get_children:
            if grp.getShapes():
                self.all_mesh.append(grp)
                self.all_mesh.append(str(grp.nodeName()))

            else:
                self.check_all_skin_group(grp)

    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info

    @record_time(__file__)
    def run_check(self):
        try:
            if not self.dialog.mod_asset['sg_asset_type'] in ['chr', 'crd', 'asm','prp','env']:
                return ""

            if not cmds.objExists('|master|poly|hi'):
                return u'没有找到 |master|poly|hi 组。'

            l_meshes = cmds.listRelatives('|master|poly|hi', ad=True, type='mesh', path=True)
            if not l_meshes:
                return ""

            for asset_name in self.dialog.d_assets_info.keys():
                if self.dialog.d_assets_info[asset_name]['type'] in ['chr','prp','env', 'crd']:
                    #  find tag: asymm
                    # sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
                    sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
                    if 'face_edge' in sg_info['tag_list']:
                        print "face edge skip"
                        return ''

            # Is ther a Lead check mark?
            if pm.objExists('td_name_check'):
                n = pm.PyNode('td_name_check')
                if n.hasAttr('asset') and n.getAttr('asset') == self.dialog.entity['name']:
                    return ""

            l_invalid_meshes = []
            l_invalid_faces = []

            for mesh_node in l_meshes:
                sl = om.MSelectionList()
                sl.add(mesh_node)
                mesh_dag = sl.getDagPath(0)
                mesh_mfn = om.MFnMesh(mesh_dag)

                for i in range(mesh_mfn.numPolygons):
                    if mesh_mfn.polygonVertexCount(i) > 4:
                        l_invalid_meshes.append(mesh_node)
                        l_invalid_faces.append(mesh_node + '.f[' + str(i) + ']')

            l_invalid_meshes = list(set(l_invalid_meshes))

            if len(l_invalid_meshes) > 0:
                cmds.select(l_invalid_faces, r=True)
                return u'有些polygon几何体有多于4条棱的面:\n' + ', '.join(l_invalid_meshes) + u'\n 可以找组长用Lead Check 跳过检测'


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
