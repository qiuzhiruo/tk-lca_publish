# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description: 
#
########################################################################################

import traceback
import pymel.core as pm
import sys
import os


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查被选择的资产。"
        self.description = u"选择资产的组(可以多选),每个组代表一个同名资产。\n检查这个资产是否有model任务。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            self.dialog.d_assets_info = {}
            l_roots = pm.ls(sl=True)
            if len(l_roots) == 0:
                return u"请选择一些要 publish 的资产。"

            tokens = self.dialog.publish_root.split('/')
            i = tokens.index('asset')
            asset_root = '/'.join(tokens[:i+1])
            
            error_list=''

            for root in l_roots:
                # Check if the asset exists 
                asset_name = root.name().split('|')[-1]
                asset = self.dialog.sg.find_one('Asset', [['project', 'is', self.dialog.project], ['code', 'is', asset_name]], ['sg_asset_type', 'sg_manual_lod'])
                if not asset:
                    error_list+= u"未能发现项目中有名为: " + asset_name + u"的资产。请与pm核对，或者先跳过择 " + root.name() + u"节点。"
                    continue
                if not asset['sg_asset_type']:
                    error_list+= u"未能获得资产 "+ asset_name + u" 的类型。请与pm核对，或者先跳过择 " + root.name() + u"节点。"
                    continue
                # Check if the model task exists
                task = self.dialog.sg.find_one('Task', [['project', 'is', self.dialog.project], ['entity', 'is', asset], ['content', 'is', 'model']])
                if not task:
                    error_list+= u"未能发现资产: " + asset_name + u" 的 model 任务。请与pm核对，或者先跳过 " + root.name() + u"节点。"
                    continue
                publish_dir = asset_root + '/' + asset['sg_asset_type'] + '/' + asset_name + '/mod/publish'
                if not os.path.isdir(publish_dir):
                    error_list+= u"未能发现资产: " + asset_name + u" 的 publish 文件夹。请与pm核对，或者先跳过 " + root.name() + u"节点。"
                    continue
                
                parent = root.getParent()
                self.dialog.d_assets_info[asset_name] = {'node': root,
                                                         'node_name': root.name().split('|')[-1],
                                                         'parent': parent,
                                                         'asset': asset,
                                                         'task': task,
                                                         'type': asset['sg_asset_type'],
                                                         'lod': asset['sg_manual_lod'],
                                                         'publish_dir': publish_dir,
                                                         'version_name': '',
                                                         'version_dir': '',
                                                         'tank_file': '',
                                                         'thumbnail': '',
                                                         'translation': (0.0, 0.0, 0.0),
                                                         'rotation': (0.0, 0.0, 0.0),
                                                         'v_info': None}
            
            
            
            if error_list:
                return error_list
            


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


