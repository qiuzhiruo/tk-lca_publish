# -*- coding:utf-8 -*-
import json
import os.path
import maya.cmds as cmds
import pymel.core as pm
from production import shotgun_connection
from proc.function_running_time import record_time


sg = shotgun_connection.Connection('get_project_info').get_sg()


class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出face pass 信息"
        self.description = u"导出face pass 信息，标记 face_pass tag"
        return

    def _get_hierarchy(self, node_path):
        """
        递归获取真实层级树。
        如果是 Mesh，直接返回名字放入列表。
        如果是 Group，返回 {组名: [子节点层级]}，完美保留大纲结构。
        """
        result = []
        # 获取当前节点的直接子节点 (只找下一层)
        children = cmds.listRelatives(node_path, children=True, type='transform', fullPath=True) or []

        for child in children:
            short_name = child.split('|')[-1]

            # 检查这个子节点有没有 shape (以此判断是实体模型还是空组)
            if cmds.listRelatives(child, shapes=True):
                # 是模型：直接以字符串形式加入列表
                result.append(short_name)
            else:
                # 是组：递归往下找，并将结果包裹成字典加入列表
                result.append({short_name: self._get_hierarchy(child)})

        return result


    def get_clt_grp_info(self):
        clt_info = {}
        for c in pm.listRelatives("|master|shape", c=1):
            if c.name().startswith('CLT_'):
                clt_info.update({c.name(): [i.rstrip('Shape') for i in cmds.listRelatives(c.name(), ad=1, f=True, type='mesh')]})
        return clt_info


    @record_time(__file__)
    def proceed(self):
        asset = self.dialog.sg.find_one("Asset", [['project', 'is', self.dialog.project], ['code', 'is', self.dialog.entity['name']]], ['id', 'tags', 'sg_diffculty2', 'sg_asset_type', 'tag_list'])
        tag_list = asset.get("tag_list", [])
        if asset.get('sg_asset_type') == 'crd' or (tag_list and "fur_pass" in tag_list):
            face_pass_grp = '|master|shape|crd_face_pass_grp'
            if not pm.ls(face_pass_grp):
                return ''
            crd_pass_info_file = os.path.join(self.dialog.version_dir, 'crd_face_pass.json')
            crd_info = {}
            for pass_name in cmds.listRelatives('|master|shape|crd_face_pass_grp', c=True):
                pass_path = '|master|shape|crd_face_pass_grp|{}'.format(pass_name)
                crd_info.update({pass_name: [i.rstrip('Shape') for i in cmds.listRelatives(pass_path, ad=1, f=True, type='mesh')]})

            with open(crd_pass_info_file, 'w') as f:
                f.write(json.dumps(crd_info, indent=4, encoding='utf-8'))

            return ''


        face_pass_grp = '|master|shape|face_pass_grp'
        if not pm.ls(face_pass_grp):
            return ''
        tag_name = 'face_pass'
        face_pass_info_file = os.path.join(self.dialog.version_dir, 'face_pass.json')

        # 调用递归函数读取所有层级
        face_pass_info = {'face_pass_grp': {}}

        # 获取第一层主组 (如 face_default_grp, face_a_grp 等)
        top_groups = cmds.listRelatives(face_pass_grp, children=True, type='transform', fullPath=True) or []

        for grp in top_groups:
            grp_name = grp.split('|')[-1]
            # 调用递归函数，将生成的层级树挂载到主组名下
            face_pass_info['face_pass_grp'][grp_name] = self._get_hierarchy(grp)

        clt_info = self.get_clt_grp_info()
        if clt_info:
            face_pass_info.update({'clt_grp': clt_info})

        with open(face_pass_info_file, 'w') as f:
            f.write(json.dumps(face_pass_info, indent=4, encoding='utf-8'))

        if str(asset.get('sg_diffculty2')) not in ['3'] or asset.get('sg_asset_type') != 'chr':
            return ''
        tag = sg.find_one(
        'Tag',
        [['name', 'is', tag_name]],
        ['id']
        )

        # 不存在就创建
        if not tag:
            tag = sg.create(
                'Tag',
                {
                    'name': tag_name
                }
            )

        asset.get('tags', []).append(tag)
        sg.update(
        'Asset',
        asset['id'],
        {
            'tags': asset.get('tags', [])
        }
        )
        return ''

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
