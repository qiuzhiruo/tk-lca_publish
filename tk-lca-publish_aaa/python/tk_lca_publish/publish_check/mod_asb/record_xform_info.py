# -*- coding:utf-8 -*-

import traceback
import os
import re
import pymel.core as pm
import sys
from xml.etree import ElementTree
import tempfile
import publish_process.gen.sgXml_parser as sgxml


# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"记录位移信息"
        self.description = u"记录位移信息。"
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
        diff_assets = []
        add_assets = []
        old_keys = old_assets.keys()

        for asset_name in new_assets:
            if asset_name in old_keys:
                if not old_assets[asset_name] == new_assets[asset_name]:
                    diff_assets.append(asset_name + '_AR')
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

    def get_latest_version(self, publish_dir, task_name=''):

        if os.path.exists(publish_dir):
            version_num = []
            for sub_file in os.listdir(publish_dir):
                if task_name in sub_file:
                    match = re.search(r'v(\d+)', sub_file)
                    if match:
                        version_num.append(int(match.group(1)))
            if version_num:
                return int(max(version_num))
        return

    def run_check(self):
        try:
            try:
                mod_version = self.get_latest_version(self.dialog.publish_root, 'model')
            except Exception as e:
                return ''

            if not mod_version:
                return ''
            assert_name = os.path.basename(pm.sceneName().split('.')[0])
            mod_path = os.path.join(self.dialog.publish_root, '{}.mod.model.v{:03d}'.format(assert_name, mod_version))
            # l_attrs = pm.listAttr('|master')
            # if not ('modVersion' in l_attrs and 'modPath' in l_attrs):
            #     return u"没有找到 Mod Version 和 Mod Path 属性，无法对比模型大小位移。"

            if str(mod_version) in ['000'] or not os.path.exists(os.path.join(self.dialog.publish_root, '{}.mod.model'.format(assert_name))):
                return ""
            mesh_xml = os.path.join(mod_path, 'scene_graph_xml', assert_name + '.xml')
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
            if diff_assets:
                self.dialog.ar_info['xform_change'] = diff_assets
                self.dialog.ar_msg += u'有{}个资产位置发生了变动:\n{}\n'.format(len(diff_assets), '\n'.join(diff_assets))

                print('ar_info=========>', self.dialog.ar_info)

            if self.dialog.ar_msg:
                self.dialog.ar_msg = assert_name + u'与上一版本{}相比:\n'.format(mod_version) + self.dialog.ar_msg

            return ""
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
