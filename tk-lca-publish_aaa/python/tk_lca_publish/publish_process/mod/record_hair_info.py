# -*- coding:utf-8 -*-
import maya.cmds as cmds
import pymel.core as pm
import os
import json
import hashlib
import maya.api.OpenMaya as om
from proc.function_running_time import record_time


class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录毛发信息"
        self.description = u"记录毛发信息"
        return

    def get_hierarchy(self, node):
        children = pm.listRelatives(
            node,
            c=True,
            type='transform'
        ) or []
        result = []
        groups = {}
        meshes = []
        for child in children:
            shapes = pm.listRelatives(
                child,
                s=True,
                type='mesh'
            ) or []
            # mesh节点
            if shapes:
                meshes.append(child.name())
            # group节点
            else:
                groups[child.name()] = self.get_hierarchy(child)
        # 如果下面只有mesh，直接返回list
        if meshes and not groups:
            return meshes
        # group继续保留dict
        groups.update({
            m: []
            for m in meshes
        })
        return groups

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

    @record_time(__file__)
    def proceed(self):
        asset_name = self.dialog.entity.get('name')
        asset_info = self.dialog.sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name'].lower()], ['code', 'is', asset_name]], ['sg_diffculty2', 'sg_asset_type'])
        if str(asset_info.get('sg_diffculty2')) != '3' or asset_info.get('sg_asset_type') != 'chr':
            return ''

        mod_grp = pm.ls('|master|shape|to_cfx|hair_grp')
        hair_info_json = os.path.join(self.dialog.publish_root, self.dialog.version_name, 'hair_info.json')

        hair_info = {}
        if not mod_grp:
            with open(hair_info_json, 'w') as f:
                f.write(json.dumps(hair_info, indent=4))
            return ''
        hair_types = pm.listRelatives('|master|shape|to_cfx|hair_grp', c=True)
        for hair_type in hair_types:
            hair_info[hair_type.name()] = self.get_hierarchy(hair_type)
            # hair_info.update({hair_type.name(): [i.name() for i in pm.listRelatives(hair_type, c=True)]})

        for h_mesh in pm.listRelatives('|master|shape|to_cfx|hair_grp', ad=True, typ='mesh'):
            hair_info.update({h_mesh.name(): self.get_mesh_topo(h_mesh)})

        with open(hair_info_json, 'w') as f:
            f.write(json.dumps(hair_info, indent=4))
        return ''

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
