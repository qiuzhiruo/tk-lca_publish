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
        self.check_name = u"模型是否在世界坐标中心"
        self.description = u"|master组内的所有的几何体在世界坐标中心，。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                proj_name = self.dialog.project

                asset = self.dialog.sg.find_one("Asset", [['project', 'is', proj_name],
                                                          ['code', 'is', asset_name]],
                                                ['sg_asset_type', 'tag_list'])
                if asset['sg_asset_type'] != 'chr':
                    return ''
                # 加 tag 也跳过
                if 'skip_check_world_center' in asset['tag_list']:
                    return ''

                #  rig有版本也跳过
                task_e = self.dialog.sg.find_one('Task', [['project', 'is', proj_name],
                                                          ['entity', 'name_is', self.dialog.entity['name']],
                                                    ['content', 'is', 'rigging']], ['id'])
                version_filters = [
                    ['sg_task', 'is', {'type': 'Task', 'id': task_e['id']}]
                ]
                versions = self.dialog.sg.find('Version', version_filters, ['id', 'code'])
                if versions:
                    print('rig有版本跳过')
                    return ''

                node = '|master'
                if not cmds.objExists(node):
                    return u'没有找到 |master 组。'

                bbox = cmds.xform(node, query=True, boundingBox=True, worldSpace=True)
                center_x = (bbox[0] + bbox[3]) / 2.0
                center_z = (bbox[2] + bbox[5]) / 2.0
                # 检查 X, Z 的绝对值是否都在容差范围内
                epsilon = 0.01
                at_center = (abs(center_x) < epsilon and abs(center_z) < epsilon)
                if not at_center:
                    return "当前模型|master不在世界坐标中心，请将物体移动到世界坐标中心, \n 也可找组长加tag： skip_check_world_center 跳过"
            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            node = '|master'
            if not cmds.objExists(node):
                return u'没有找到 |master 组。'

            # 获取世界坐标下的bbox：[xmin, ymin, zmin, xmax, ymax, zmax]
            bbox = cmds.xform(node, query=True, boundingBox=True, worldSpace=True)
            # 计算 X 和 Z 的bbox中心点
            center_x = (bbox[0] + bbox[3]) / 2.0
            center_z = (bbox[2] + bbox[5]) / 2.0
            cmds.xform(node, translation=[-center_x, 0, -center_z], relative=True, worldSpace=True)

            cmds.makeIdentity(apply=True, t=True, r=True, s=True)
            cmds.delete(constructionHistory=True)

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


