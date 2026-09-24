# -*- coding:utf-8 -*-

import pymel.core as pm
from proc.function_running_time import record_time


class MG:
    HEADS = ['head_eyes_open_geo', 'head_eye_open']


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"一二三级角色自动减面 和 导出to_lay"
        self.description = u"一二三级角色自动减面和导出to_lay"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        self.dialog.temp_head = ''
        asset = self.dialog.sg.find_one("Asset", [['project', 'is', self.dialog.project], ['code', 'is', self.dialog.entity['name']]], ['sg_diffculty2', 'sg_asset_type'])
        if str(asset['sg_diffculty2']) not in ['1', '2', '3'] or asset['sg_asset_type'] != 'chr':
                return ''
        if str(asset['sg_diffculty2']) in ['1', '2']:
            if not pm.ls(MG.HEADS):
                return u"一二级角色没有{}这些中的其中一个不能进行自动减面。".format(','.join(MG.HEADS))
            else:
                self.dialog.temp_head = pm.ls(MG.HEADS)[0].name()
        try:
            if not pm.pluginInfo('PolygonCruncher', loaded=True, q=True):
                pm.loadPlugin('PolygonCruncher.mll')
            return ''

        except:
            return u'PolygonCrunche 插件未安装.'

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


