# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.09
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
        self.check_name = u"确保 UV 在 0-100 区域内。"
        self.description = u"确保 poly 和 shape 组下所有面的 uv 都在正向象限且不超过 100 。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            self.l_bad_uvs = []
            self.CN_uvset = {}

            for asset_name in self.dialog.d_assets_info.keys():
                sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
                if 'skip_uv_range' in sg_info['tag_list']:
                    print "skip skip_uv_range check"
                    return ''
                root = self.dialog.d_assets_info[asset_name]['node']

                if root.fullPath() == '|master':
                    l_meshes = pm.listRelatives('|master', ad=True, type='mesh')
                else:
                    l_meshes = pm.listRelatives(root, ad=True, type='mesh')

                for n in l_meshes:
                    bad_list = []
                    uvset_list = pm.polyUVSet(n, allUVSets=True, q=True)
                    if not uvset_list:
                        continue
                    uvset_list.reverse()
                    for uvset in uvset_list:
                        if self.dialog.os == 'win':
                            for s in str(uvset):
                                if  '\u4e00' <= s <= '\u9fa5':
                                    bad_list.append(uvset)
                                    self.CN_uvset[str(n)] = bad_list
                        elif self.dialog.os == 'linux':
                            if '?' in str(uvset):
                                bad_list.append(uvset)
                                self.CN_uvset[str(n)] = bad_list
                        pm.polyUVSet(n, currentUVSet=True, uvSet=uvset)
                        node_name = pm.listRelatives(n, p=True)[0].name()
                        uv_bbx = pm.polyEvaluate( node_name,  boundingBox2d=True)
                        if uv_bbx[0][0] < 0.0 or uv_bbx[0][1] >100.0 or uv_bbx[1][0] < 0.0 or uv_bbx[1][1] >100.0:
                            if uvset == 'map1':
                                self.l_bad_uvs.append(node_name)
                            else:
                                try:
                                    if not uvset.startswith('srf'):
                                        pm.polyUVSet(n, d=True, uvSet=uvset)
                                except Exception,e:
                                    print e
                                    
            if len(self.l_bad_uvs) >0:
                return u"uv超出 0-100 象限的面: \n" + u'\n'.join(self.l_bad_uvs)
            if self.CN_uvset:
                return u"以下物体的uvset含有中文: \n" + u'\n'.join(self.CN_uvset.keys())

            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            if self.CN_uvset:
                print u'uvset有中文不能自动修复'
                return u'uvset的名字包含中文，不能自动判断哪个uvset是正确的，需要手动修复'
            if self.l_bad_uvs:
                result = pm.confirmBox(
                    title='警告',
                    message='如果是手动制作的uv请手动修复下，自动修复会重新展uv!! \n 是否继续自动修复?',
                    button=['是', '否'],  # 自定义按钮文字
                    defaultButton='是',  # 默认高亮的按钮
                    cancelButton='否'  # 点击 X 等同于哪个按钮
                )

                if result == '否':
                    return ''
                for node_name in self.l_bad_uvs:
                    pm.polyAutoProjection('%s.f[*]'% node_name )
                    pm.mel.eval('DeleteAllHistory;')

                    pm.select(node_name + ".map[:]")
                    pm.polyEditUV( pivotU=0.5, pivotV=0.5, scaleU=0.8, scaleV=0.8)
                    pm.select(node_name)
                    pm.mel.eval('DeleteAllHistory;')
                    pm.select(cl=True)

            return ''
        except:
            return traceback.format_exc()

    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


