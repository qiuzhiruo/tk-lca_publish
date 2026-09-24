#! -*- coding:utf-8 -*-

import traceback
from cfx.flgDynamicAsset import submit_cmd as submit


class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"创建flg动态毛发资产"
        self.description = u"根据gas动态资产驱动cfx静态资产"

    def proceed(self):
        try:
            proj_name = self.dialog.project['name'].lower()
            asset_name = self.dialog.entity['name']
            task_name = self.dialog.task['name']

            if 'cloth' in task_name:
                return ''

            if self.dialog.asset_type == 'flg':
                submit.build(proj_name, asset_name, task_name)
            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description