# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Huazhuo Yu
#
# Date: 2013.10
#
# Description: Check to see if too many (more than 5) faces are connected on a vertex.
#
########################################################################################

import traceback

import maya.OpenMaya as om
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查set是否和shotgun匹配。"
        self.description = u"检查asm资产的set是否和shotgun子资产匹配，如果不匹配请自行修改本地文件的set，或联系制片修改shotgun的当前资产的子资产信息。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:

            mod_asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]],
                                                ['sg_asset_type', 'assets'])
            self.dialog.asm_set = []

            if len(mod_asset['assets']) == 0:
                return ""
            if not mod_asset['sg_asset_type'] in ['asm']:
                return ""

            if not pm.objExists('|master|poly|hi'):
                return u'没有找到 |master|poly|hi 组。'

            if not pm.objExists('asm_set'):
                return u'没有找到 asm_set。'



            asm_set = pm.PyNode('asm_set')
            sub_assets_node = [a.name() for a in asm_set.members()]
            self.dialog.asm_set = sub_assets_node

            error_asset_set = []
            for sub_asset in mod_asset['assets']:
                if not sub_asset['name'] in sub_assets_node:
                    error_asset_set.append(sub_asset['name'])

            if error_asset_set != []:
                return u'asm_set 下没有找到 子资产的 set：' + u' ,'.join(error_asset_set)

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
