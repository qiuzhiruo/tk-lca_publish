# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: Check to see if any vertice are overlapping to each other.
#
########################################################################################

import traceback
import os
import maya.cmds as cmds
import maya.mel as mel
import json
import pymel.core as pm
import maya.api.OpenMaya as om
import production.pipeline.lcProdProj as lcp
import re
import sys
from xml.etree import ElementTree
import tempfile

import publish_process.gen.sgXml_parser as sgxml


# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"和上一版本的资产位移进行比对。"
        self.description = u"防止对资产的误操作数据流入下游。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def export_tmp_xml(self):
        asb_xml_path = tempfile.mktemp() + '.xml'
        root = pm.PyNode('|master')

        # export asb xml file
        xml = sgxml.SgXmlParser()
        xml.exportXml(root, asb_xml_path)
        return asb_xml_path

    def xml_to_xfrom(self, mesh_xml):
        tree = ElementTree.parse(mesh_xml)
        root = tree.getroot()
        l_assets = root.getiterator("instance")
        assets_xfrom = {}
        for asset in l_assets:
            xform_attr = asset.getiterator('xform')[0].attrib
            assets_xfrom[asset.attrib['name']] = [xform_attr[k] for k in xform_attr.keys()]

        return assets_xfrom

    def diff_assets_dict(self, old_assets, new_assets):
        diff_assets = []
        add_assets = []
        old_keys = old_assets.keys()

        for asset_name in new_assets:
            if asset_name in old_keys:
                if not old_assets[asset_name] == new_assets[asset_name]:
                    diff_assets.append(asset_name)
            else:
                add_assets.append(asset_name)
        return diff_assets,add_assets

    def select_AR(self,assets_list):
        pm.select(cl=1)
        for asset in assets_list:
            if pm.objExists(asset):
                pm.select(asset, tgl=1)
            else:
                asset_str = asset.replace('.', ':') + '_AR'
                if pm.objExists(asset_str):
                    pm.select(asset_str, tgl=1)


    def run_check(self):
        try:
            try:
                mod_version = pm.getAttr('|master.modVersion')
                mod_path = pm.getAttr('|master.modPath').replace('\\', '/')
            except Exception as e:
                return ''
            l_attrs = pm.listAttr('|master')
            if not ('modVersion' in l_attrs and 'modPath' in l_attrs):
                return u"没有找到 Mod Version 和 Mod Path 属性，无法对比模型大小位移。"
            assert_name = os.path.basename(mod_path.split('.')[0])
            if not mod_version or not mod_path:
                return ''
            if str(mod_version) in ['000', '001']:
                return ""
            mesh_xml = os.path.join(os.path.dirname(mod_path), 'scene_graph_xml', assert_name + '.xml')
            if sys.platform.startswith('linux'):
                mesh_xml = mesh_xml.replace('Z:/', '/mnt/proj/')

            if not os.path.isfile(mesh_xml):
                return u"没有找到模型对应的 xml 文件: " + mesh_xml

            old_xfrom_dict = self.xml_to_xfrom(mesh_xml)
            self.old_xfrom_dict = old_xfrom_dict
            if len(old_xfrom_dict) == 0:
                return u'没有找到上一版本的资产位移（xfrom）'

            tem_xml = self.export_tmp_xml()
            new_xfrom_dict = self.xml_to_xfrom(tem_xml)
            if len(new_xfrom_dict) == 0:
                return u'资产位移（xfrom）获取失败' + tem_xml

            diff_assets,add_assets = self.diff_assets_dict(old_xfrom_dict, new_xfrom_dict)
            self.dialog.ar_info['xform_change'] = diff_assets

            print('ar_info=========>', self.dialog.ar_info)

            if not len(diff_assets) == 0:
                self.select_AR(diff_assets)
                return u'这几个资产相较上一版本有位置变化 ： ' + ' ,'.join(diff_assets) + u'如果是无意改动，可以使用自动修复可以复原选中物体的上一版位移。'
            return ""
        except:
            return traceback.format_exc()
    
    def run_fix(self):
        '''Auto Fix'''
        try:
            old_xfrom_dict=self.old_xfrom_dict
            select_assets=pm.ls(sl=1)
            for asset in select_assets:
                asset_name=asset.name().replace(':','.').replace('_AR','')
                if asset_name in old_xfrom_dict.keys():
                    asset_xfrom=[float(f) for f in old_xfrom_dict[asset_name][0].split(' ')]
                    pm.xform( asset, a=True, matrix=asset_xfrom, objectSpace=True)

                    print asset,asset_xfrom

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
