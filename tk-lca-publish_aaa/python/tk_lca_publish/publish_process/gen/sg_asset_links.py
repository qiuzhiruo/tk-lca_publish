# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.08
#
# Description:
#
############################################

import os
import traceback
import proc.parse_shot_xml as parser
import proc.xml_scene_summary as xml_scene_summary
reload(parser)

import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.d_assets = {}
        
        self.process_name = u"更新 Shotgun 上资产与镜头/场的关系链接。(暂停)"
        self.description = u"更新 Shotgun 上资产与镜头/场的关系链接。(暂停)"
        return


    def proceed(self):
        try:
            shot_info = self.dialog.entity

            if not pm.objExists('|assets'):
                return ""
            #
            # Get Top level reference and assembly reference nodes
            self.get_top_ref_node()
            #
            # update shot link
            '''
            self.dialog.sg.update('Shot', shot_info['id'], {'assets': self.d_assets.values()})

            # update sequence link
            seq_info = self.dialog.sg.find_one('Sequence', [['shots', 'is', shot_info]], ['assets', 'code'] )
            if not seq_info:
                return ""

            d_seq_assets = self.d_assets.copy()
            for asset in seq_info['assets']:
                if not d_seq_assets.has_key(asset['name']):
                    d_seq_assets[asset['name']] = asset

            if len(d_seq_assets) > len(seq_info['assets']):
                self.dialog.sg.update('Sequence', seq_info['id'], {'assets':d_seq_assets.values()})
            '''

            # if an asset is animated or big or close to the camera, it's a major asset. Otherwise it's a minor asset.
            #self.scene_xml_path = self.dialog.version_dir + '/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
            if os.path.isfile(self.scene_xml_path):
                #self.set_major_minor_assets(shot_info)
                self.scene_description()
            return ""

        except:
            return traceback.format_exc()

    def get_top_ref_node(self):
        """
        """
        l_ref_asset_nodes = filter(None, set([h for h in pm.ls('*:master', rn=True, type='transform') if h.isChildOf(pm.PyNode('|assets'))]))
        l_ar_asset_nodes = filter(None, set([h for h in pm.ls('*_AR', type='assemblyReference')]))
        self.d_assets = {}

        l_asset_names = []
        for asset_node in l_ref_asset_nodes:
            asset_name = os.path.basename(pm.referenceQuery(asset_node,  filename=True, wcn=True))[:-3]
            l_asset_names.append(asset_name)

        for asset_node in l_ar_asset_nodes:
            asset_name = os.path.basename(asset_node.getAttr('definition'))[:-3]
            l_asset_names.append(asset_name)
        
        l_asset_names = list(set(l_asset_names))
        for asset_name in l_asset_names:
            asset = self.dialog.sg.find_one('Asset', [['code', 'is', asset_name], ['project', 'is', self.dialog.project]], ['sg_poly_count_hi', 'sg_asset_type'])
            if asset:
                self.d_assets[ asset_name ] = asset
            else:
                print '==> unable find asset on shotgun:', asset_name
        
        self.scene_xml_path = self.dialog.version_dir + '/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
        #return self.d_assets

    def set_major_minor_assets(self, shot_info):
        """
        """
        ani_xml_path = self.dialog.version_dir + '/ani_assets.xml'

        l_ani_assets = parser.get_ani_assets(ani_xml_path)

        cam_angle = parser.get_cam_angle(self.scene_xml_path)
        d_asset_angles = parser.get_assets_angle(self.scene_xml_path)
        if cam_angle is None:
            return ""
        d_major = {}
        d_minor = {}
        for asset_name, l_angles in d_asset_angles.iteritems():
            if not self.d_assets.has_key(asset_name):
                self.d_assets[asset_name] = self.dialog.sg.find_one('Asset', [['code', 'is', asset_name], ['project', 'is', self.dialog.project]], ['sg_poly_count_hi', 'sg_asset_type'])
            asset = self.d_assets[asset_name]
            if asset:
                if max(l_angles) > cam_angle * 0.01 or asset_name in l_ani_assets:
                    d_major[ asset['id'] ] = asset
                elif max(l_angles) > cam_angle * 0.0005:
                    d_minor[ asset['id'] ] = asset

        self.dialog.sg.update('Shot', shot_info['id'], {'sg_major': d_major.values()})
        self.dialog.sg.update('Shot', shot_info['id'], {'sg_minor': d_minor.values()})

        return


    def scene_description(self):
        txt = self.dialog.w_publish.plainTextEdit_auto_description.toPlainText()
        if txt != '':
            txt += '\n'

        txt += xml_scene_summary.summarize(self.scene_xml_path, self.dialog.sg, self.dialog.project, self.d_assets)
        self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(txt)

        return


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


