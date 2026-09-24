# -*- coding:utf-8 -*-

import os
import  sys
import pymel.core as pm
import maya.cmds as cmds
from proc.function_running_time import record_time


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查当前资产是否正在自动发布"
        self.description = u"子资产更新会连带父亲资产更新，该检查项就是在查是否有因为子资产更新触发的当前资产的发布任务."
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        self.asset_name = os.path.basename(pm.sceneName()).split('.')[0]
        self.asset_info = self.get_asset_relation_info(self.asset_name)

        if self.asset_info['asset_sg_mod_parent_assets_assets']:

            if 'publishing_automatically' in self.asset_info['tag_list']:
                return u'资产更新中，请稍后再尝试.\n 如果等待时间过长，请联系td'

        return ''

    def get_asset_relation_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['asset_sg_mod_parent_assets_assets', 'sg_mod_parent_assets', 'tag_list'])
        return asset_info

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty


