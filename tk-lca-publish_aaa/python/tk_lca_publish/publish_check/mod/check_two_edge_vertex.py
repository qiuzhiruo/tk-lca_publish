# -*- coding:utf-8 -*-
import os
import re
import maya.OpenMaya as om
import maya.cmds as cmds
from proc.function_running_time import record_time


class MG:
    ignore_type = ['flg']


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"模型内部的点不能只连接两条边"
        self.description = u"模型内部的点不能只连接两条边skip tag: skip_two_edge"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        file_name = cmds.file(q=True, sn=True)
        if not file_name:
            return ''
        asset_name = os.path.basename(file_name).split('.')[0]
        pattern = r'asset/(\w{num})/{asset}'.format(num='{3}', asset=asset_name)
        if re.search(pattern, file_name):
            if re.search(pattern, file_name).group(1) in MG.ignore_type:
                print('============flg asset skip=============')
                return ''
        sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
        if sg_info:
            if 'skip_two_edge' in sg_info['tag_list']:
                print("=======skip check_two_edge_vertex==========")
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
            ver_iter = om.MItMeshVertex(dag_path)
            while not ver_iter.isDone():
                edge_list = om.MIntArray()
                face_list = om.MIntArray()
                ver_iter.getConnectedEdges(edge_list)
                ver_iter.getConnectedFaces(face_list)

                if len(edge_list) == len(face_list) == 2:
                    err_info.append('{}.vtx[{}]'.format(mesh, ver_iter.index()))

                ver_iter.next()

        if err_info:
            err_msg = u'模型内部存在只连接两条线的顶点,分别是:\n{}\n 如果确认没问题sg上给该资产加标签"skip_two_edge"即可跳过。'\
                      .format('\n'.join(err_info))
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


