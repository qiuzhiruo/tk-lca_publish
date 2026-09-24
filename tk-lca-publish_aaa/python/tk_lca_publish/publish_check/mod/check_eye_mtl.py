# -*- coding:utf-8 -*-

########################################################################################
#
# Author: liangyue
#
# Date: 2026.07
#
# Description: 对衣服 检查角色资产眼球是否有材质。
#
########################################################################################
import os
import json
import pymel.core as pm
import maya.cmds as cmds
import traceback

import re
from proc.function_running_time import record_time
from proc import get_materials_info
reload(get_materials_info)
from proc.get_materials_info import get_mesh_materials, is_material_transparent, is_file_node_texture_exists


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查角色资产眼球是否有材质。"
        self.description = u"检查角色资产眼球是否有材质: L/R_eyeballs_inside 必须连接两个及以上材质球，或者一个有贴图的材质球； L/R_eyeball_geo连接的材质球必须是透明的. \n 跳过tag： skip_eye_mtl"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            # 基础资产过滤
            asset_name = self.dialog.entity.get('name')
            asset_info = self.dialog.sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name'].lower()],
                                                           ['code', 'is', asset_name]],
                                                 ['sg_diffculty2', 'sg_asset_type', 'tag_list'])

            if asset_info.get('sg_asset_type') != 'chr':
                return ''
            tag_list = asset_info.get('tag_list')
            if tag_list:
                if 'skip_eye_mtl' in tag_list or ' skip_eye_mtl' in tag_list:
                    return ''

            eyeballs_inside_nodes = ['|master|poly|hi|mesh_grp|skin_grp|R_eyeball_geo_grp|R_eyeballs_inside', '|master|poly|hi|mesh_grp|skin_grp|L_eyeball_geo_grp|L_eyeballs_inside']
            eyeball_geo_nodes = ['|master|poly|hi|mesh_grp|skin_grp|R_eyeball_geo_grp|R_eyeball_geo', '|master|poly|hi|mesh_grp|skin_grp|L_eyeball_geo_grp|L_eyeball_geo']
            no_mtl_list = []
            no_tex_nodes = []
            # 眼球
            for node in eyeballs_inside_nodes:
                if not cmds.objExists(node):
                    continue
                mtl_list = get_mesh_materials(node)
                mtl_num = len(mtl_list)
                if mtl_num >= 2:
                    continue
                elif mtl_num == 1:
                    # 检查是否有贴图
                    file_nodes = cmds.listConnections(mtl_list[0], type='file') or []
                    tex_list = []
                    for f in file_nodes:
                        if not is_file_node_texture_exists(f) and str(f) not in no_tex_nodes:
                            no_tex_nodes.append(str(f))
                        tex = cmds.getAttr(f + '.fileTextureName')
                        tex_list.append(tex)
                    if not tex_list:
                        no_mtl_list.append(node)
                else:
                    no_mtl_list.append(node)
            # 眼球外圈透明的mesh
            no_transparency_list = []
            for node in eyeball_geo_nodes:
                if not cmds.objExists(node):
                    continue
                m_list = get_mesh_materials(node)
                # 没有材质
                if not m_list:
                    no_mtl_list.append(node)
                    continue
                # 检查是否至少有一个透明材质
                is_transparent = False
                for material in m_list:
                    if is_material_transparent(material):
                        is_transparent = True
                        break
                if not is_transparent:
                    no_transparency_list.append(node)
            if no_tex_nodes:
                print('no_tex_nodes:', no_tex_nodes)
                return '下面这些file节点上贴图不存在：\n ' + '\n'.join(no_tex_nodes)
            if no_mtl_list:
                return '下面这些mesh没有材质，请赋好材质后再上传：\n ' + '\n'.join(no_mtl_list)
            if no_transparency_list:
                return '下面这些mesh的材质需要是透明的：\n ' + '\n'.join(no_transparency_list)

            return ""

        except Exception as e:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty







