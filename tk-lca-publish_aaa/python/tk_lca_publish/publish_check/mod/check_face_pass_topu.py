# -*- coding:utf-8 -*-

import os
import json
import datetime
import tempfile

import pymel.core as pm
from PySide2 import QtWidgets

from proc.function_running_time import record_time
# from proc.get_versions import get_task_versions
from proc import topu_change_check
reload(topu_change_check)
from proc.topu_change_check import generate_mesh_structure_xml, compare_mesh_topology_xml


class StdCheck:
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"变脸角色毛发壳topu检查"
        self.description = u"变脸角色毛发壳检查， 与上一个版本相比不能减少，不能改topu. 跳过tag: skip_fp_topu(毛发减少不可被跳过, 拓补变化可被跳过)"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        self.dialog.hair_info = {}
        return

    @record_time(__file__)
    def run_check(self):
        asset_name = self.dialog.entity.get('name')
        asset_info = self.dialog.sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name'].lower()], ['code', 'is', asset_name]], ['sg_diffculty2', 'sg_asset_type', 'tag_list'])
        # if asset_info and 'skip_fp_topu' in asset_info['tag_list']:
        #     return ''
        if self.dialog.project['name'].lower() in ['lic']:
            return ''
        if str(asset_info.get('sg_diffculty2')) != '3' or asset_info.get('sg_asset_type') != 'chr':
            return ''

        face_pass_topu_xml = os.path.join(self.dialog.publish_root, '{}.mod.model'.format(asset_name), 'face_pass_topu.xml')
        print('face_pass_topu_xml--->', face_pass_topu_xml)
        face_pass_grp = pm.ls('|master|shape|face_pass_grp')
        if not face_pass_grp:
            return ''

        # 第一版不做比较
        if not os.listdir(self.dialog.publish_root):
            return ''

        if not os.path.exists(face_pass_topu_xml):
            return ''

        tmp = tempfile.gettempdir()

        tmp_xml = os.path.join(tmp, "%s_face_pass.xml" % (datetime.datetime.now().strftime("%Y%m%d%H%M")))
        print('tmp_xml--->', tmp_xml)
        generate_mesh_structure_xml(
            root_node='|master|shape|face_pass_grp',
            output_xml=tmp_xml
        )

        result = compare_mesh_topology_xml(
            old_xml=face_pass_topu_xml,
            new_xml=tmp_xml,
            check_hair=True
        )
        print('Topo Changed:', result['topology_changed'])
        print('Added:', result['added'])
        print('Removed:', result['removed'])

        if result['removed']:
            return u"当前场景与上一个版本相比减少了: \n" + '\n'.join(result['removed'])
        # if result['added']:
        #     return u"当前场景与上一个版本相比增加了: \n" + '\n'.join(result['added'])
        if result['topology_changed']:
            if asset_info and 'skip_fp_topu' in asset_info['tag_list']:
                return ''
            pm.select(result['topology_changed'])
            return u'下面这些mesh拓补变化了: \n{}\n'.format('\n'.join(result['topology_changed']))

        os.remove(tmp_xml)

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


