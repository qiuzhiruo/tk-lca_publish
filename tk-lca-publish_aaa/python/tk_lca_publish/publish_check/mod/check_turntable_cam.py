# -*- coding:utf-8 -*-

import sys
import re
import os
import traceback
import pymel.core as pm
import glob
from proc.function_running_time import record_time


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查相机。"
        self.description = u"场景内的组只有master和turntable_cam,turntable_cam只允许有一个。skip tag: turntable_cams_skip"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                if self.dialog.d_assets_info[asset_name]['type'] != 'chr':
                    return u""

            asset_tags = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['tags'])
            tags = [t['name'] for t in asset_tags['tags']]
            if "turntable_cams_skip" in tags:
                return u""
            node_names = set(node.name() for node in pm.ls(assemblies=True))
            turntable_cams = [name for name in node_names if 'turntable_cam' in name]
            if len(turntable_cams)!=1:
                return u"当前场景内turntable_cam的数量不为1。\n如果需要跳过请联系总监或组长在shotgun tags上标注 '' turntable_cams_skip ''"
            else:
                return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty


