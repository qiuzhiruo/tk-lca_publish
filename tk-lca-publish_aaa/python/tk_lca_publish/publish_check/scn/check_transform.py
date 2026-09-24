# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: liang yue
#
# Date: 2026.05
#
# Description: The model stands above the origion.
#
########################################################################################

import traceback
import maya.cmds as cmds
import maya.mel as mel
from proc.function_running_time import record_time


# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查 master节点 上是否有位移'
        self.description = u"检查 master节点 上是否有位移。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            asset_info = self.dialog.sg.find_one("Asset", [['project', 'is', self.dialog.project],
                                                           ['code', 'is', self.dialog.entity['name']]],
                                                 ['sg_asset_type', 'tag_list'])

            if 'skip_scn_transform' in asset_info['tag_list']:
                return ''

            node = '|master'
            if not cmds.objExists(node):
                return u'没有找到 |master 组。'

            translate = cmds.getAttr('master.translate')[0]  # 返回 [(x, y, z)]
            rotate = cmds.getAttr('master.rotate')[0]
            scale = cmds.getAttr('master.scale')[0]
            is_identity = (
                    translate == (0.0, 0.0, 0.0) and
                    rotate == (0.0, 0.0, 0.0) and
                    scale == (1.0, 1.0, 1.0)
            )
            if not is_identity:
                return "master节点上不能位移, \n 也可找组长加tag： skip_scn_transform 跳过"
            return ""

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


