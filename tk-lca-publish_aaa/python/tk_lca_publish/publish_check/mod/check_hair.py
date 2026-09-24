# -*- coding:utf-8 -*-

import os
import json
import pymel.core as pm
import hashlib
import maya.api.OpenMaya as om
from PySide2 import QtWidgets
from proc.function_running_time import record_time
from proc.get_versions import get_task_versions


def get_scene_hair_info(root_node):
    """
    遍历指定根节点下的层级结构，收集所有包含 mesh 的 group 及其对应的 meshes 列表。
    采用 BFS（广度优先遍历）。

    :param root_node: PyNode, 遍历的根节点
    :return: dict, 格式为 { group_name: [mesh_names, ...] }
    """
    result = {}
    if not root_node:
        return result

    queue = [root_node]

    while queue:
        current_node = queue.pop(0)

        children = pm.listRelatives(
            current_node,
            c=True,
            type='transform',
            fullPath=True
        ) or []

        meshes = []
        for child in children:
            shapes = pm.listRelatives(child, s=True, type='mesh') or []
            if shapes:
                meshes.append(child.name())
            else:
                queue.append(child)

        if meshes:
            result[current_node.name()] = meshes

    return result


def compare_hair_info(json_file, check_grp):
    """
    比对 JSON 文件记录与当前场景中 hair 层级的变化，严格兼容新旧两种 JSON 格式。

    :return:
        less_list: list, 格式为 "group|mesh"，旧格式无 group 时为 "|mesh"
        add_list:  list, 格式为 "group|mesh"，旧格式无 group 时为 "|mesh"
    """
    less_list = []
    add_list = []

    # 1. 校验输入文件与节点
    if not os.path.exists(json_file):
        return less_list, add_list

    grp = pm.ls(check_grp)
    if not grp:
        return less_list, add_list

    # 2. 读取历史数据
    with open(json_file, 'r') as f:
        try:
            old_info = json.load(f)
        except json.JSONDecodeError:
            return less_list, add_list

    old_hair_data = old_info.get('head_hair', {})
    current_hair_data = get_scene_hair_info(grp[0])

    all_groups = set(old_hair_data.keys()) | set(current_hair_data.keys())

    for group in all_groups:
        old_meshes = set(old_hair_data.get(group, []))
        new_meshes = set(current_hair_data.get(group, []))

        # 减少的 mesh
        for mesh in (old_meshes - new_meshes):
            less_list.append("{}|{}".format(group, mesh))

        # 增加的 mesh
        for mesh in (new_meshes - old_meshes):
            add_list.append("{}|{}".format(group, mesh))

    return less_list, add_list


class StdCheck:
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"三级角色毛发检查"
        self.description = u"主要检查是否有减少，要通知道到rig. 跳过tag: skip_hair_check(毛发减少不可被跳过)"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        self.dialog.hair_info = {}
        return

    def get_mesh_topo(self, mesh):
        face_count = pm.polyEvaluate(mesh, face=True)
        if face_count == 0:
            return hashlib.md5(' ').hexdigest()

        sl = om.MSelectionList()
        sl.add(mesh.fullPath())   # ← 这里
        dag = sl.getDagPath(0)
        mfn = om.MFnMesh(dag)

        v = mfn.getVertices()
        v_str0 = '[' + ', '.join(map(str, v[0])) + ']'
        v_str1 = '[' + ', '.join(map(str, v[1])) + ']'

        return hashlib.md5((v_str0 + ' ' + v_str1)).hexdigest()

    def check_topo(self, json_file):
        # hair_mesh = pm.listRelatives('|master|shape|to_cfx|hair_grp', ad=True, typ='mesh')
        # json_file = self.dialog.publish_root + '/' + self.dialog.entity['name'] + '.mod.model/hair_info.json'
        if not os.path.exists(json_file):
            return []
        with open(json_file, 'r') as f:
            old_hair_info = json.loads(f.read())

        error_mesh = []
        for hair_mesh in pm.listRelatives('|master|shape|to_cfx|hair_grp', ad=True, typ='mesh'):
            hair_mesh_name = hair_mesh.name()
            if hair_mesh_name not in old_hair_info:
                continue
            if str(old_hair_info.get(hair_mesh_name)) != str(self.get_mesh_topo(hair_mesh)):
                error_mesh.append(hair_mesh_name)

        return error_mesh


    @record_time(__file__)
    def run_check(self):
        asset_name = self.dialog.entity.get('name')
        asset_info = self.dialog.sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name'].lower()], ['code', 'is', asset_name]], ['sg_diffculty2', 'sg_asset_type', 'tag_list'])
        if asset_info and 'skip_hair_check' in asset_info['tag_list']:
            return ''
        if str(asset_info.get('sg_diffculty2')) != '3' or asset_info.get('sg_asset_type') != 'chr':
            return ''

        hair_info_json = os.path.join(self.dialog.publish_root, '{}.mod.model'.format(asset_name), 'hair_info.json')
        hair_grp = pm.ls('|master|shape|to_cfx|hair_grp')

        # 第一版不做比较
        if not os.listdir(self.dialog.publish_root):
            return ''

        if not os.path.exists(hair_info_json):
            return ''
        with open(hair_info_json, 'r') as f:
            old_hair_info = json.loads(f.read())

        if not hair_grp:
            return ''
        old_hair_data = old_hair_info.get('head_hair', {})
        err_msg = u'相较于上一版当前场景'
        if isinstance(old_hair_data, list):
            less_info = {}
            add_info = {}
            hair_types = pm.listRelatives('|master|shape|to_cfx|hair_grp', c=True)
            for hair_type in hair_types:

                hair_objs = [i.name() for i in pm.listRelatives(hair_type, c=True)]
                old_hair_objs = old_hair_info.get(hair_type.name(), [])

                if list(set(old_hair_objs) - set(hair_objs)):
                    less_info.update({hair_type: list(set(old_hair_objs) - set(hair_objs))})
                if list(set(hair_objs) - set(old_hair_objs)):
                    add_info.update({hair_type: list(set(hair_objs) - set(old_hair_objs))})

            print('less_info---->', less_info)
            for hair_type, less_objs in less_info.items():
                err_msg += u'{0}下缺少: \n{1}\n'.format(hair_type, '\n'.join(less_objs))
            if less_info:
                return err_msg

            if add_info:
                for hair_type_a, add_objs in add_info.items():
                    err_msg += u'相较于上一版当前场景{0}下增加了: \n{1}\n'.format(hair_type_a, '\n'.join(add_objs))
                    QtWidgets.QMessageBox.warning(self.dialog, u"提示", err_msg)

        elif isinstance(old_hair_data, dict):
            less_nodes, add_nodes = compare_hair_info(
                hair_info_json,
                '|master|shape|to_cfx|hair_grp'
            )
            err_msg = u'相较于上一版当前场景, |master|shape|to_cfx|hair_grp 下'
            if less_nodes:
                err_msg += u'缺少:\n' + '\n'.join(less_nodes)
                return err_msg
            if add_nodes:
                err_msg += u'增加:\n' + '\n'.join(add_nodes)
                QtWidgets.QMessageBox.warning(self.dialog, u"提示", u"当前三级角色的毛发与上一版本相比有增加\n\n{}".format(err_msg))

        error_topo = self.check_topo(hair_info_json)
        if error_topo:
            err_msg += u'下面这些mesh拓补变化了: \n{}\n'.format('\n'.join(error_topo))
            self.dialog.hair_info = err_msg
            # flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
            # asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
            if asset_info:
                if 'skip_hair_check' in asset_info['tag_list']:
                    # get cfx version
                    cfx_versions = get_task_versions(self.dialog.project['name'].upper(), asset_name, 'cfx')
                    print('had cfx_versions--->', len(cfx_versions))
                    if cfx_versions:
                        # QtWidgets.QMessageBox.warning(self.dialog, u"提示", u"当前资产已有发布的 cfx版本，毛发减少和拓补变化 会影响cfx制作，减少可以把不用的隐藏掉")
                        return '当前资产已有发布的 cfx版本，毛发减少和拓补变化 会影响cfx制作，减少可以把不用的隐藏掉'
                    return ''
            return err_msg

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


