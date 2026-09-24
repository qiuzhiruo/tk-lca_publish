# -*- coding:utf-8 -*-
import traceback
import os
from proc.function_running_time import record_time
from proc.get_versions import get_task_versions


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"1，2级角色第一版发布时勾选 是否引用一次"
        self.description = u"1，2级角色第一版发布时勾选 是否引用一次"
        return

    @record_time(__file__)
    def proceed(self):
        try:
            project_name = self.dialog.project['name']
            if project_name.lower() in ['lic']:
                return ''
            asset_name = self.dialog.entity['name']
            asset_info = self.dialog.sg.find_one("Asset", [['project', 'is', self.dialog.project], ['code', 'is', asset_name]], ['sg_diffculty2', 'sg_asset_type', 'sg_is_reference_one_time'])
            if not asset_info:
                return ''
            if asset_info.get('sg_asset_type') != 'chr' or str(asset_info.get('sg_diffculty2')) not in ['1', '2'] or asset_info.get('sg_is_reference_one_time'):
                return ''
            mod_versions = get_task_versions(project_name.upper(), asset_name, 'mod')
            if len(mod_versions) == 1:
                self.dialog.sg.update('Asset', asset_info['id'], {'sg_is_reference_one_time': True})
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
