# -*- coding:utf-8 -*-

import os
import json
import datetime
import tempfile

import pymel.core as pm
from PySide2 import QtWidgets

from proc.function_running_time import record_time
from proc.get_versions import get_task_versions

from proc import topu_change_check
reload(topu_change_check)
from proc.topu_change_check import generate_mesh_structure_xml, compare_mesh_topology_xml
from proc.get_versions import get_task_versions


class StdCheck:
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"变脸角色衣服topu检查"
        self.description = u"变脸角色衣服检查， 与上一个版本相比不能减少，不能改topu." \
                           u" 跳过tag: skip_clt_topu(拓补变化可被跳过, 资产已有发布的 cfx版本衣服减少不可被跳过;" \
                           u"已有发布的 cfx版本，毛发减少和拓补变化 会影响cfx制作，减少可以把不用的隐藏掉,不可跳过)"
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
        sg_asset_type = asset_info.get('sg_asset_type')

        if sg_asset_type not in ['chr', 'crd']:
            return ''
        asset_type = asset_info.get('sg_asset_type')

        if asset_type == 'chr':
            if str(asset_info.get('sg_diffculty2')) != '3':
                return ''

        elif asset_type == 'crd':
            if 'crd_face_pass' not in asset_info.get('tag_list', []):
                return ''
        cloth_grp = '|master|poly|hi|mesh_grp|cloth_grp'
        if not pm.objExists(cloth_grp):
            return ''

        mesh_xml = os.path.join(self.dialog.publish_root, '{}.mod.model'.format(asset_name), 'mesh.xml')
        # 第一版不做比较
        if not os.listdir(self.dialog.publish_root):
            return ''

        if not os.path.exists(mesh_xml):
            return ''
        # 第一版精模也不对比
        mod_versions = get_task_versions(self.dialog.project['name'].upper(), asset_name, 'mod')
        if mod_versions:
            last_v = mod_versions[0]
            if last_v['tag_list'] and '粗模' in last_v['tag_list']:
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

        #

        if result['removed']:
            if 'skip_clt_topu' in asset_info.get('tag_list', []):
                return ''
                # cfx_versions = get_task_versions(self.dialog.project['name'].upper(), asset_name, 'cfx')
                # print('had cfx_versions--->', len(cfx_versions))
                # if not cfx_versions:
                #     return ''
                # else:
                #     return '当前资产已有发布的 cfx版本，衣服减少和拓补变化 会影响cfx制作，减少可以把不用的隐藏掉,不可跳过'
            if 'crd_face_pass' in asset_info.get('tag_list', []):
                if 'skip_clt_topu' in asset_info.get('tag_list', []):
                    return ''
                cfx_versions = get_task_versions(self.dialog.project['name'].upper(), asset_name, 'cfx')
                print('had cfx_versions--->', len(cfx_versions))
                if not cfx_versions:
                    return ''
            return u"当前场景与上一个版本相比减少了: \n" + '\n'.join(result['removed'])
        # if result['added']:
        #     return u"当前场景与上一个版本相比增加了: \n" + '\n'.join(result['added'])
        if result['topology_changed']:
            if asset_info and 'skip_clt_topu' in asset_info['tag_list']:
                cfx_versions = get_task_versions(self.dialog.project['name'].upper(), asset_name, 'cfx')
                print('had cfx_versions--->', len(cfx_versions))
                if cfx_versions:
                    # QtWidgets.QMessageBox.warning(self.dialog, u"提示", u"当前资产已有发布的 cfx版本，毛发减少和拓补变化 会影响cfx制作，减少可以把不用的隐藏掉")
                    return '当前资产已有发布的 cfx版本，衣服减少和拓补变化 会影响cfx制作，减少可以把不用的隐藏掉,不可跳过'
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


