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
        self.check_name = u"和上一版本的资产添加进行比对。"
        self.description = u"防止对资产的误操作数据流入下游。"
        self.auto_fix = False
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
        add_assets = []
        old_keys = old_assets.keys()

        for asset_name in new_assets:
            if not asset_name in old_keys:
                add_assets.append(asset_name)
        return add_assets

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
            l_attrs = pm.listAttr('|master')
            if not ('modVersion' in l_attrs and 'modPath' in l_attrs):
                return u"没有找到 Mod Version 和 Mod Path 属性，无法对比模型大小位移。"

            mod_version = pm.getAttr('|master.modVersion')
            mod_path = pm.getAttr('|master.modPath').replace('\\', '/')
            assert_name = os.path.basename(mod_path.split('.')[0])
            if not mod_version or not mod_path:
                return ''
            if mod_version == '000':
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

            add_assets = self.diff_assets_dict(old_xfrom_dict, new_xfrom_dict)

            if not len(add_assets) == 0:
                self.select_AR(add_assets)
                return u'这几个资产是新增资产 ： ' + ' ,'.join(add_assets) + u'如果是无意改动，可以手动删除。'
            return ""
        except:
            return traceback.format_exc()
    
    def run_fix(self):
        '''Auto Fix'''
        try:
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
