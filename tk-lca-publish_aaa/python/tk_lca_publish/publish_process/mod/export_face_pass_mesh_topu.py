# -*- coding:utf-8 -*-
import maya.cmds as cmds
import pymel.core as pm
import os
import json
import hashlib
import maya.api.OpenMaya as om
from proc.function_running_time import record_time
from proc.topu_change_check import generate_mesh_structure_xml

class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录face_pass毛发topu信息"
        self.description = u"记录face_pass毛发topu信息, check tupo"
        return

    @record_time(__file__)
    def proceed(self):
        if self.dialog.version_tag == u"粗模":
            return ''
        asset_name = self.dialog.entity.get('name')
        asset_info = self.dialog.sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name'].lower()], ['code', 'is', asset_name]], ['sg_diffculty2', 'sg_asset_type'])
        if str(asset_info.get('sg_diffculty2')) != '3' or asset_info.get('sg_asset_type') != 'chr':
            return ''

        mod_grp = pm.ls('|master|shape|face_pass_grp')
        if not mod_grp:
            return ''
        face_pass_topu_xml = os.path.join(self.dialog.publish_root, self.dialog.version_name, 'face_pass_topu.xml')

        generate_mesh_structure_xml('|master|shape|face_pass_grp', face_pass_topu_xml)

        return ''

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
