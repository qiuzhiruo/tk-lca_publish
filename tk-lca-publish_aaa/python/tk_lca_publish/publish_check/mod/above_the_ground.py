# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
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
        self.check_name = u"模型站在地面之上。"
        self.description = u"|master|poly组内的所有的几何体的脚部紧贴地面，上下不超过0.01个单位。如果距离过远，可以用自动修复放到原点。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                asset_type = self.dialog.d_assets_info[asset_name]['type']
                if asset_type=='env':
                    return ""

                if not cmds.objExists('|master|poly'):
                    return u'没有找到 |master|poly 组。'

                bbox_min_y = cmds.getAttr('|master|poly.boundingBoxMin')[0][1]
                if abs(bbox_min_y) > 0.01 :
                    return u"模型最低处离地面 "+str(bbox_min_y ) + u" 个单位。"

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''

        try:
            if not cmds.objExists('|master|poly'):
                return u'没有找到 |master|poly 组。'

            bbox_min_y = cmds.getAttr('|master|poly.boundingBoxMin')[0][1]
            if abs(bbox_min_y) > 0.01:
                cmds.move( 0, (bbox_min_y * -1), 0, "|master|poly", r=True)

            # Freeze transform and set pivots
            cmds.select('|master|poly')
            mel.eval('FreezeTransformations;')
            cmds.select(cl=True)

            l_trans = cmds.listRelatives('|master|poly', ad=True, type='transform', fullPath=True)
            l_trans.append('|master|poly')
            l_trans.sort()

            for trans in l_trans:
                cmds.xform(trans, zeroTransformPivots=True)

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


