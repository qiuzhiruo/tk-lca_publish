# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.05
#
# Description: 
#
############################################

import traceback

import os
import re
import pymel.core as pm
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"资产模型高低模需要匹配。"
        self.description = u"针对 chr, prp, env, veh 的检查。\n如果资产有多组模型(hi/md/lo/proxy), 它们的bounding box 是否\"基本\"一致。两个bounding box 的xyz方向上各自可以有5%的偏差。\n比如hi模的bbox的两个角的x分别为-40.0, 60.0，则低模的两个角的x必须在(-45.0,-35.0) 和 (55.0, 65.0)之间。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def lod_match(self, asset_type, hi, lod):
            l_unmatched_cord = []
            asset_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])


            if asset_type in ['chr', 'prp', 'env', 'veh']:

                if self.vis_ctrl != None:
                    self.vis_ctrl.setAttr('hiLoVis', 0)
                else:
                    hi.setAttr('v', True)

                (hi_min, hi_max) = hi.boundingBox()

                if self.vis_ctrl != None:
                    self.vis_ctrl.setAttr('hiLoVis', 1)
                else:
                    lod.setAttr('v', True)

                (lo_min, lo_max) = lod.boundingBox()

                # Debug: print bounding box
                print 'hi:', hi_min, hi_max
                print 'lo:', lo_min, lo_max

                hi_x = hi_max[0] - hi_min[0]
                hi_y = hi_max[1] - hi_min[1]
                hi_z = hi_max[2] - hi_min[2]

                if hi_x < 0.00001:
                    hi_x = 0.00001
                if hi_y < 0.00001:
                    hi_y = 0.00001
                if hi_z < 0.00001:
                    hi_z = 0.00001

                dif_x_min = hi_min[0] - lo_min[0]
                dif_y_min = hi_min[1] - lo_min[1]
                dif_z_min = hi_min[2] - lo_min[2]
                dif_x_max = hi_max[0] - lo_max[0]
                dif_y_max = hi_max[1] - lo_max[1]
                dif_z_max = hi_max[2] - lo_max[2]

                if abs(dif_x_min) > 0.05 and abs(dif_x_min/ hi_x) > 0.05:
                    l_unmatched_cord.append('x_min')
                if abs(dif_y_min) > 0.05 and abs(dif_y_min/ hi_y) > 0.05:
                    l_unmatched_cord.append('y_min')
                if abs(dif_z_min) > 0.05 and abs(dif_z_min/ hi_z) > 0.05:
                    l_unmatched_cord.append('z_min')

                if abs(dif_x_max) > 0.05 and abs(dif_x_max/ hi_x) > 0.05:
                    l_unmatched_cord.append('x_max')
                if abs(dif_y_max) > 0.05 and abs(dif_y_max/ hi_y) > 0.05:
                    l_unmatched_cord.append('y_max')
                if abs(dif_z_max) > 0.05 and abs(dif_z_max/ hi_z) > 0.05:
                    l_unmatched_cord.append('z_max')

            if len(l_unmatched_cord) > 0:
                return u"高低模不匹配: " + ' '.join(l_unmatched_cord)
            else:
                return ''


    @record_time(__file__)
    def run_check(self):

        try:
            if pm.objExists('Visibility'):
                self.vis_ctrl = pm.PyNode('Visibility')
                current_vis = self.vis_ctrl.getAttr('hiLoVis')
            else:
                self.vis_ctrl = None
                current_vis = None

            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                asset_type = self.dialog.d_assets_info[asset_name]['type']

                if not pm.objExists(root.name() + '|poly'):
                    continue

                l_res = pm.listRelatives(root.name() + '|poly')
                if len(l_res) < 2:
                    continue

                if not pm.objExists(root.name() + '|poly|hi'):
                    return asset_name + u'没有 hi 模.'

                hi = pm.PyNode(root.name() + '|poly|hi')
                for res in l_res:
                    if res.nodeName() != 'hi':
                        result = self.lod_match(asset_type, hi, res)
                        if result != '':
                            print hi.name(),res.name(),result
                            error_str=u"{0} 和 {1}" .format(hi.name() , res.name() + result)
                            return error_str

            if self.vis_ctrl != None:
                self.vis_ctrl.setAttr('hiLoVis', current_vis)

            return ""

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



