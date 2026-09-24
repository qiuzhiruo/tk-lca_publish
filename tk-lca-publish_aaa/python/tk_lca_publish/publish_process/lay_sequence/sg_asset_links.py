# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.07
#
# Description:
#
############################################

import os
import traceback
import shutil
import pymel.core as pm

import lay.lca_camera_sequencer.functions as functions_cs
import ani.lca_layer_manager.functions as functions_lm


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"更新 Shotgun 上资产与镜头/场的关系链接。(暂停)"
        self.description = u"更新 Shotgun 上资产与镜头/场的关系链接。(暂停)"
        return

    def _get_shotgun_assets(self, root_nodes):
        assets = {}
        if not root_nodes:
            return assets

        for asset_node in root_nodes:
            node_type = pm.objectType(asset_node)
            if node_type == 'transform':
                asset_path = pm.referenceQuery(asset_node, filename=True, wcn=True)
            elif node_type == 'assemblyReference':
                asset_path = asset_node.getAttr('definition')
            else:
                continue
            asset_name = os.path.basename(asset_path)
            asset_name = os.path.splitext(asset_name)[0]
            asset = self.dialog.sg.find_one('Asset',
                                            [['code', 'is', asset_name],
                                             ['project', 'is', self.dialog.project]])
            if asset:
                assets[asset['id']] = asset
            else:
                print '==> unable find asset on shotgun:', asset_name
        return assets

    def proceed(self):
        try:
            '''
            assemblies = pm.ls('*_AR', type='assemblyReference')
            assembly_assets = self._get_shotgun_assets(assemblies)
            for data in self.dialog.shots_preview_data:
                masters = functions_cs.get_tagged_assets(data['shot_info']['code'])
                assets = self._get_shotgun_assets(masters)
                assets.update(assembly_assets)
                self.dialog.sg.update('Shot', data['shot_info']['id'], {'assets': assets.values()})

            seq_info = self.dialog.sg.find_one('Sequence', [['id', 'is', self.dialog.entity['id']]], ['assets'])
            if not seq_info:
                return ""

            masters = functions_lm.getMasters(referencedNodes=True)
            assets = self._get_shotgun_assets(masters)
            assets.update(assembly_assets)
            for asset in seq_info['assets']:
                assets.setdefault(asset['id'], asset)

            if len(assets.keys()) > len(seq_info['assets']):
                self.dialog.sg.update('Sequence', seq_info['id'], {'assets':assets.values()})
            '''
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
