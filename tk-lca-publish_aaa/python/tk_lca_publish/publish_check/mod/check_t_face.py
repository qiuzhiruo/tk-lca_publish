# -*- coding:utf-8 -*-
import os
import re
import maya.OpenMaya as om
import maya.cmds as cmds
import getpass
from proc.function_running_time import record_time


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查T型面"
        self.description = u"一条边不能同时在两个以上的面上，否则会导致无法展UV。skip tag: skip_t_face"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        for asset_name in self.dialog.d_assets_info.keys():
            asset_type = self.dialog.d_assets_info[asset_name]['type']
            if asset_type == 'flg':
                return ''

            file_name = cmds.file(q=True, sn=True)
            asset_name = os.path.basename(file_name).split('.')[0]

            sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
            if sg_info:
                if 'skip_t_face' in sg_info['tag_list']:
                    print("=======skip skip_t_face==========")
                    return ''

            if not cmds.objExists('|master|poly|hi'):
                return ''
            mesh_list = cmds.listRelatives('|master|poly|hi', typ='mesh', ad=True, f=True)
            err_info = []

            for mesh in mesh_list:
                selection_list = om.MSelectionList()
                selection_list.add(mesh)
                dag_path = om.MDagPath()
                selection_list.getDagPath(0, dag_path)
                edg_iter = om.MItMeshEdge(dag_path)
                while not edg_iter.isDone():
                    face_list = om.MIntArray()
                    edg_iter.getConnectedFaces(face_list)

                    if len(face_list) > 2:
                        for face_index in face_list:
                            err_info.append('{}.f[{}]'.format(mesh, face_index))

                    edg_iter.next()

            if err_info:
                err_msg = u'存在T型面:\n{}'.format('\n'.join(err_info))
                cmds.select(err_info)
                return err_msg
            return ''

    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info

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


