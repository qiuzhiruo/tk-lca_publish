# -*-coding:utf-8-*-
"""
 @Time : 4/23/23 5:06 PM
 @Author : Taka(xutao)
"""


import traceback
import os
import re
import maya.cmds as cmds
import pymel.core as pm
import cfx.cfx_felt_pipeline.hair_pass_utils as hpu
try:
    import xgenm as xgm
    import xgenm.xgGlobal as xgg
except:
    pass


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查生长面命名是否符合规范"
        self.description = u"检查lrs崂山项目的生长面命名是否是使用Import Xgen Preset工具创建的"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            if 'cloth' in self.dialog.task['name'] or pm.ls(type='pgYetiMaya'):
                return ''

            proj = self.dialog.project['name'].lower()
            asset = self.dialog.entity['name']

            bad_str = ''
            if hpu.is_felt(proj, asset):
                collections = xgm.palettes()
                if not collections:
                    return u'这个文件没有collection!'

                for collection in collections:
                    descriptions = xgm.descriptions(collection)
                    for description in descriptions:
                        patches = xgm.boundGeometry(collection, description)
                        for patch in patches:
                            if not pm.objExists(patch):
                                bad_str += u' %s --> %s 的生长面 %s 不存在或命名错误，请检查是否使用了工具创建\n' % (
                                collection, description, patch)
                            if not patch.startswith(asset) or not patch.endswith('_growth'):
                                bad_str += u' %s --> %s 的生长面 %s 的命名不正确 应该以资产名开头 _growth结尾 请检查是否使用了工具创建\n' % (
                                collection, description, patch)
                            shape = patch.split('%s_' % asset, 1)[1].split('_growth')[0]
                            if not pm.objExists(shape):
                                bad_str += u' %s --> %s 的生长面 %s 与关联的mesh %s 命名不一致 请检查\n' % (
                                collection, description, patch, shape)

            return bad_str

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty