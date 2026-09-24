# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.02
#
# Description: As the description shows below
#
############################################

import traceback
import pymel.core as pm
from maya import cmds
import xgenm as xg
from xgenm.ui.xgDescriptionEditor import refreshDescriptionEditor


class ASSET_ATTRIBUTE_CONFIG(object):
    CUSTOM_ATTRS = ['custom_float_uparamcoord',
                    'custom_float_vparamcoord',
                    'custom_float_curve_id',
                    'custom_vector_lc_faceid',
                    'custom_vector_lc_v',
                    'custom_float_lc_faceid_length']
    PALETTE_ATTRS = ['rigPass', ]


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查xgen毛发属性命名"
        self.description = u"检查xgen毛发属性命名"
        self.auto_fix = True
        self.duty = u"艺术家本人"

    def _get_palettes(self):
        """获取所有调色板"""
        return xg.palettes()

    def _get_description_attrs(self, palette, description):
        """获取描述的自定义属性"""
        return [i for i in xg.customAttrs(palette, description, 'RendermanRenderer')
                if '__arnold' not in i]

    def _get_palette_attrs(self, palette):
        """获取调色板的自定义属性"""
        return cmds.listAttr(palette, ud=1) or []

    def _get_useless_palette_attrs(self, palette):
        """获取调色板上不需要的属性"""
        attrs = self._get_palette_attrs(palette)
        return [attr for attr in ASSET_ATTRIBUTE_CONFIG.PALETTE_ATTRS if attr in attrs]

    def _get_useless_description_attrs(self, palette, description):
        """获取描述上不需要的属性"""
        attrs = self._get_description_attrs(palette, description)
        return [attr for attr in attrs if attr not in ASSET_ATTRIBUTE_CONFIG.CUSTOM_ATTRS]

    def run_check(self):
        try:
            if 'cloth' in self.dialog.task['name'] or pm.ls(type='pgYetiMaya'):
                return ''

            palettes = self._get_palettes()
            if not palettes:
                return u'这个文件没有collection!'

            bad_str = ''  # 累积错误信息
            for palette in palettes:
                if self._get_useless_palette_attrs(palette):
                    bad_str += palette + u"有多余的Rig Pass属性需要删除！\n"

                for description in xg.descriptions(palette):
                    if not self._get_description_attrs(palette, description):
                        bad_str += u'没有自定义uv和id属性,快去bake一下!\n'
                        continue

                    useless = self._get_useless_description_attrs(palette, description)
                    if useless:
                        bad_str += description + u' 有多余的属性: ' + ','.join(useless) + '\n'

            return bad_str
        except:
            return traceback.format_exc()

    def run_fix(self):
        try:
            palettes = self._get_palettes()
            if not palettes:
                return u'这个文件没有collection!'

            for palette in palettes:
                useless_attrs = self._get_useless_palette_attrs(palette)
                if useless_attrs:
                    for attr in useless_attrs:
                        cmds.deleteAttr(palette, attribute=attr)

                for description in xg.descriptions(palette):
                    for attr in self._get_useless_description_attrs(palette, description):
                        xg.remCustomAttr(attr, palette, description, "RendermanRenderer")

            refreshDescriptionEditor()
            return ''

        except:
            return traceback.format_exc()

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty