# -*- coding:utf-8 -*-

import maya.cmds as cmds
from proc.function_running_time import record_time


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查未缝合的点"
        self.description = u"检查未缝合的点。skip tag: skip_unmerged_vertices"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        for asset_name in self.dialog.d_assets_info.keys():
            asset = self.dialog.sg.find_one("Asset", [['project', 'is', self.dialog.project], ['code', 'is', self.dialog.entity['name']]], ['sg_diffculty2', 'sg_asset_type'])
            if str(asset['sg_diffculty2']) != '3' or asset['sg_asset_type'] != 'chr':
                    return ''

            sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
            if sg_info:
                if 'skip_unmerged_vertices' in sg_info['tag_list']:
                    return ''

            cmds.select(cl=1)
            error_vtx = []
            for mesh in cmds.listRelatives('|master|poly|hi', ad=1, typ='mesh'):
                vtx_data = self.find_unmerged_vertices(mesh)
                for a, b in vtx_data:
                    error_vtx.append(a)

            if error_vtx:

                cmds.modelEditor('modelPanel4', e=True, displayAppearance='wireframe')
                cmds.select(cl=1)
                cmds.select(error_vtx)
                return u'已选中未缝合的点，请检查修复，若确认无误，可跳过该检查。'
            return ''


    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info

    def find_unmerged_vertices(self, mesh):

        verts = cmds.ls(mesh + '.vtx[*]', fl=True)

        pos_dict = {}

        result = []

        for vtx in verts:

            pos = cmds.pointPosition(vtx, w=True)

            # 做距离容差
            key = (
                round(pos[0], 4),
                round(pos[1], 4),
                round(pos[2], 4)
            )

            if key in pos_dict:
                result.append((pos_dict[key], vtx))
            else:
                pos_dict[key] = vtx

        return result

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

