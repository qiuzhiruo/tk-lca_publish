# -*- coding:utf-8 -*-

import os
import traceback
import pymel.core as pm
import re

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"复用资产描述信息"
        self.description = u"复用资产描述信息"
        return

    def proceed(self):

        proj_name = self.dialog.project['name'].lower()
        for asset_name in self.dialog.d_assets_info.keys():
            if 'modPath' not in pm.listAttr(asset_name):
                continue
            mod_path = pm.getAttr('{}.modPath'.format(asset_name))
            if not mod_path:
                continue

            p = re.search('/projects/(\w+)/asset/\w+/(\w+)/mod', mod_path.replace('\\', '/'))
            if not p:
                continue

            old_proj_name = p.group(1)
            old_asset_name = p.group(2)
            if old_asset_name == asset_name and old_proj_name == proj_name:
                continue

            project = self.dialog.sg.find_one('Project', [['name', 'is', proj_name]])
            asset = self.dialog.sg.find_one('Asset', [['project', 'is', project], ['code', 'is', asset_name]])
            reuse_info = u'复用:{}.{}'.format(old_proj_name, old_asset_name)
            self.dialog.sg.update('Asset', asset['id'], {'description': reuse_info})

        return ""

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description


