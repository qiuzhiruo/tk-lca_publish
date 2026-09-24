# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: Freeze transformation for all tranform nodes; force all pivots to the origion
#
########################################################################################

import traceback
import pymel.core as pm
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"物体的坐标清零并放在坐标原点。"
        self.description = u"在master组下(包括master这个组)的物体的位移，旋转，放缩的值清零，坐标放在坐标原点。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            l_bad_trans = []
            self.sl_list = pm.ls(sl=True)
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                parent = self.dialog.d_assets_info[asset_name]['parent']
                translation = self.dialog.d_assets_info[asset_name]['translation']
                rotation = self.dialog.d_assets_info[asset_name]['rotation']

                # if root.fullPath() == '|master':
                pm.select(root, r=True)
                pm.mel.eval('makeIdentity -apply true -t 1 -r 1 -s 1 -n 0;')

                # mov sub assets to the world center
                if parent:
                    pm.parent(root, world=True)

                root.setRotation((0.0, 0.0, 0.0))
                pm.xform(root, r=True, translation=(translation[0] * -1,  translation[1] * -1, translation[2] * -1))

                # Freeze transoform - 坐标清零
                pm.select(root, r=True)
                #mel.eval('FreezeTransformations;')
                pm.mel.eval('makeIdentity -apply true -t 1 -r 1 -s 1 -n 0;')
                l_trans = pm.listRelatives(root, ad=True, type='transform')
                l_trans.append(root)

                for trans in l_trans:
                    pivots = pm.xform(trans, q=True, pivots=True)
                    for v in pivots:
                        if abs(v) > 0.001:
                            l_bad_trans.append(trans.name())

                pm.xform(root, r=True, translation=(translation[0],  translation[1], translation[2]))
                root.setRotation(rotation)
                pm.select(cl=True)

                if parent:
                    pm.parent(root, parent)

            if self.dialog.task['name'] == 'assembly':
                pm.select(self.sl_list)
            l_bad_trans = list(set(l_bad_trans))
            if len(l_bad_trans) > 0:
                if self.dialog.task['name'] != 'assembly':
                    pm.select(l_bad_trans, r=True)
                return u'物体: '+ u' '.join(l_bad_trans) + u' 的中心不在坐标原点。'

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            self.sl_list = pm.ls(sl=True)
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                parent = self.dialog.d_assets_info[asset_name]['parent']
                translation = self.dialog.d_assets_info[asset_name]['translation']
                rotation = self.dialog.d_assets_info[asset_name]['rotation']
                pm.select(root, r=True)
                pm.mel.eval('makeIdentity -apply true -t 1 -r 1 -s 1 -n 0;')
                if parent:
                    pm.parent(root, world=True)

                root.setRotation((0.0, 0.0, 0.0))
                pm.xform(root, r=True, translation=(translation[0] * -1,  translation[1] * -1, translation[2] * -1))

                l_trans = pm.listRelatives(root, ad=True, type='transform', fullPath=True)
                l_trans.append(root)
                for trans in l_trans:
                    trans.setRotatePivot((0.0, 0.0, 0.0))
                    trans.setScalePivot((0.0, 0.0, 0.0))
                    pm.xform(trans, zeroTransformPivots=True)
                    pivots = pm.xform(trans, q=True, pivots=True)

                pm.xform(root, r=True, translation=(translation[0],  translation[1], translation[2]))
                root.setRotation(rotation)

                if parent:
                    pm.parent(root, parent)

            if self.dialog.task['name'] == 'assembly':
                pm.select(self.sl_list)
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


