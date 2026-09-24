# -*- coding:utf-8 -*-
import json
import sys
import os.path

import pymel.core as pm
import xml.etree.ElementTree as ET
import hashlib
import maya.api.OpenMaya as om
from production import shotgun_connection
from proc.function_running_time import record_time


sg = shotgun_connection.Connection('get_project_info').get_sg()


class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出head信息"
        self.description = u"导出head信息与绑定的做比较，决定绑定是否要更新头颅。"
        return


    def get_head_hash(self, obj):

        position_hash = None
        position_sum = 0.0
        if isinstance(obj, int):
            obj = int(obj) - 1
            # 获取所有点
            vtxs = pm.ls('body_geo.vtx[0:{}]'.format(obj), fl=True)
            if not vtxs:
                return position_hash

            # 获取 mesh shape
            mesh = vtxs[0].node()
        else:
            if pm.ls(obj):
                mesh = pm.ls(obj)[0]
            else:
                print('-none-obj--->', obj)
                return ''

        # 转 dagPath
        sel = om.MSelectionList()
        sel.add(mesh.name())
        dagPath = sel.getDagPath(0)

        # MFnMesh
        mesh_fn = om.MFnMesh(dagPath)

        # 获取所有点（对象空间）
        all_points = mesh_fn.getPoints(om.MSpace.kObject)

        if isinstance(obj, int):
            # 拿 index
            indices = [v.index() for v in vtxs]

            # 筛选
            points = [all_points[i] for i in indices]
        else:
            points = all_points
        pos_list = []
        for pt in points:
            pos_list.append("{:.4f},{:.4f},{:.4f}".format(pt.x, pt.y, pt.z))
            position_sum += (pt.x + pt.y + pt.z)
        pos_str_full = "|".join(pos_list)
        position_hash = hashlib.md5(pos_str_full.encode('utf-8')).hexdigest()

        return position_hash


    @record_time(__file__)
    def proceed(self):
        mod_head_info = {}
        rig_info_xml = '/mnt/proj/projects/{0}/asset/chr/{1}/rig/publish/'.format(self.dialog.project['name'].lower(), self.dialog.entity['name']) + self.dialog.entity['name'] + '.rig.rigging/facial_mesh.xml'
        if sys.platform.startswith('win'):
            rig_info_xml.replace('/mnt/proj/', 'Z:/')
        if not os.path.exists(rig_info_xml):
            return ''
        all_v = os.listdir(self.dialog.publish_root)
        all_v.sort()
        old_head_info = {}
        if len(all_v) > 3:
            old_head_info_f = os.path.join(self.dialog.publish_root, all_v[-2], 'head_info.json')
            if os.path.exists(old_head_info_f):
                with open(old_head_info_f, 'r') as f:
                    old_head_info = json.loads(f.read())
        tree = ET.parse(rig_info_xml)
        root = tree.getroot()
        for mesh in root.iter('mesh'):
            full_path = mesh.get('fullPath')
            obj = full_path
            if 'facial_head_geoShape' in full_path:
                obj = int(mesh.get('vertex'))
            if not obj:
                return ''
            if not pm.objExists(obj):
                return ''
            position_hash = self.get_head_hash(obj)
            # no:代表相比上一版无变化，yes：代表有变化

            mod_head_info.update({full_path: ["no", position_hash]})

            if old_head_info.get(full_path):
                if old_head_info.get(full_path)[-1] != position_hash:
                    mod_head_info.update({full_path: ["yes", position_hash]})

        mod_head_json = os.path.join(self.dialog.version_dir, 'head_info.json')
        with open(mod_head_json, 'w') as f:
            f.write(json.dumps(mod_head_info, indent=4))
        return ''

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
