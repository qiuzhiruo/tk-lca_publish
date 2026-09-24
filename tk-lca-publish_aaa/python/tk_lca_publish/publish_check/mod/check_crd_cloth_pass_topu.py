# -*- coding:utf-8 -*-

import os
import json
import datetime
import tempfile
import platform

import pymel.core as pm
from PySide2 import QtWidgets

from proc.function_running_time import record_time
from proc.get_versions import get_task_versions

from proc import topu_change_check
reload(topu_change_check)
from proc.topu_change_check import generate_mesh_structure_xml, compare_mesh_topology_xml, _calc_mesh_topology, get_mesh_topu


class StdCheck:
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"变脸crd与其父资产topu检查"
        self.description = u"与 父资产相比 crd资产的 cloth_grp 组下（衣服） 和 body_geo 拓扑不能改变, 层级和mesh名字也不能改变，" \
                           u" 可以减少，但不能增加 mesh. " \
                           u"详细规范：https://rcn8f1ebg7ch.feishu.cn/wiki/DMXKwumIriJQyKk5wUlcPcVonRd?fromScene=spaceOverview"

        self.auto_fix = False
        self.duty = u"艺术家本人。"
        self.dialog.hair_info = {}
        return

    @record_time(__file__)
    def run_check(self):
        asset_name = self.dialog.entity.get('name')
        asset_info = self.dialog.sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name'].lower()], ['code', 'is', asset_name]], ['sg_diffculty2', 'sg_asset_type', 'tag_list', 'parents'])
        # if asset_info and 'skip_fp_topu' in asset_info['tag_list']:
        #     return ''
        project_name = self.dialog.project['name'].lower()
        if project_name in ['lic']:
            return ''
        sg_asset_type = asset_info.get('sg_asset_type')

        if sg_asset_type not in ['crd'] or 'crd_face_pass' not in asset_info.get('tag_list', []):
            return ''
        cloth_grp = '|master|poly|hi|mesh_grp|cloth_grp'
        if not pm.objExists(cloth_grp):
            return ''
        p_assets = asset_info['parents']
        if not p_assets:
            return '当前高精度变脸crd资产，制片没有标注 父资产，请联系制片标注父资产'
        p_asset = p_assets[0]['name']
        if platform.system().lower() == 'windows':
            mesh_xml = r'Z:/projects/{}/asset/chr/{}/mod/publish/{}.mod.model/mesh.xml'.format(project_name, p_asset, p_asset)

        else:
            mesh_xml = '/mnt/proj/projects/{}/asset/chr/{}/mod/publish/{}.mod.model/mesh.xml'.format(project_name, p_asset, p_asset)

        if not os.path.exists(mesh_xml):
            print('没找到mesh.xml:', mesh_xml)
            return ''

        tmp = tempfile.gettempdir()

        tmp_xml = os.path.join(tmp, "%s_cloth.xml" % (datetime.datetime.now().strftime("%Y%m%d%H%M")))
        print('tmp_xml--->', tmp_xml)
        generate_mesh_structure_xml(root_node=cloth_grp,output_xml=tmp_xml)

        result = compare_mesh_topology_xml(
            old_xml=mesh_xml,
            new_xml=tmp_xml,
            old_grp='|master|poly|hi|mesh_grp|cloth_grp',
            new_grp='|master|poly|hi|mesh_grp|cloth_grp'
        )

        print('Topo Changed:', result['topology_changed'])
        print('Added:', result['added'])
        print('Removed:', result['removed'])

        msg = u'当前资产与父资产:{}相比：'.format(p_asset)
        # if result['removed']:
        #     return u"当前场景与上一个版本相比减少了: \n" + '\n'.join(result['removed'])
        if result['added']:
            msg += u"增加了: \n" + '\n'.join(result['added'])
        if result['topology_changed']:
            pm.select(result['topology_changed'])
            msg += u'\n下面这些mesh拓补变化了: \n{}\n'.format('\n'.join(result['topology_changed']))

        os.remove(tmp_xml)
        if result['added'] or result['topology_changed']:
            return msg

        # 对比 body_geo
        body_topu = _calc_mesh_topology(pm.PyNode('body_geo'))
        body_mesh = '|master|poly|hi|mesh_grp|skin_grp|body_geo|body_geoShape'
        p_body_topu = get_mesh_topu(body_mesh, mesh_xml)
        if body_topu != p_body_topu:
            return '当前资产与父资产:{}相比：body_geo的拓扑不一致 '.format(p_asset)

        return ''

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


