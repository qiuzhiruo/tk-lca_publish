# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu, Wang Huan
#
# Date: 2015.09
#
# Description: 
#
########################################################################################

import traceback
import pymel.core as pm
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查长度小于 0.000010 的边。"
        self.description = u"可能是距离极近的两个点组成；也可能是一个点充当边的两个起点。这两种边都要清除掉。skip tag: skip_short_edge"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def check_if_flg(self):
        for asset_name in self.dialog.d_assets_info.keys():
            asset_type = self.dialog.d_assets_info[asset_name]['type']
            if asset_type == 'flg':
                return True
            else:
                return False

    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info

    @record_time(__file__)
    def run_check(self):
        try:
            self.l_short_edges = []
            self.l_bad_meshes = []

            for asset_name in self.dialog.d_assets_info.keys():
                sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
                if sg_info:
                    if 'skip_short_edge' in sg_info['tag_list']:
                        return ''
                root = self.dialog.d_assets_info[asset_name]['node']

                if root.fullPath() == '|master':
                    l_meshes = pm.listRelatives('|master', ad=True, type='mesh')
                else:
                    l_meshes = pm.listRelatives(root, ad=True, type='mesh')

                for n in l_meshes:
                    pm.select(n, r=True)
                    pm.polySelectConstraint( m=3, t=0x8000, l=True, lb=(0, 0.000010))
                    sel = pm.ls(sl=True)
                    if len(sel) > 0:
                        self.l_short_edges.extend(sel)
                        self.l_bad_meshes.append(n)

            pm.polySelectConstraint( m=3, t=0x8000, l=False, lb=(0, 0.000010))
            if len(self.l_short_edges) >0:
                pm.select(self.l_short_edges, r=True)
                return u"长度小于 0.000010 的边: \n" + u'\n'.join([str(e) for e in self.l_short_edges])

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            if not self.check_if_flg():
                for n in self.l_bad_meshes:
                    pm.select(n, r=True)
                    pm.mel.eval('polyCleanupArgList 3 { "0","1","1","0","0","0","0","0","0","1e-005","1","1e-005","0","1e-005","0","1","0" };')
                pm.mel.eval('DeleteAllHistory;')
                pm.select(cl=True)
                return ''
            else:
                return 'flg资产需艺术家手动修复,无法使用自动修复'
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


