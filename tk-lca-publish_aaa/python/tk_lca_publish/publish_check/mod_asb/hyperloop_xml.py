# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2019 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.06
#
############################################

import traceback
import os
import re
from xml.etree import ElementTree

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查Hyper Loop 提供的 XML 文件。"
        self.description = u"检查Hyper Loop 提供的 XML 文件"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            xml_path = self.dialog.w_publish_file.lineEdit_xml.text()
            if not os.path.isfile(xml_path):
                return u"无效的 xml 文件路径"

            self.dialog.hyperloop = {}
            l_invalid = []
            tree = ElementTree.parse(xml_path)
            root = tree.getroot()
            l_instances = root.getiterator('instance')
            for ins in l_instances:
                if ins.attrib.has_key('refFile') and ins.attrib.has_key('name'):
                    xml = ins.attrib['refFile']
                    abc = os.path.dirname(xml) + '/hi.abc'

                    if ins.attrib['name'].startswith("hyper_asset_"):
                        asset_info_list = ins.attrib['name'].split("_")
                        asset_info = "_".join(asset_info_list[2:-1])
                        asset = asset_info.rstrip('0123456789')
                        group = "hyperloop"

                    elif ins.attrib['name'].startswith("shotgun_asset_"):
                        asset_info_list = ins.attrib['name'].split("_")
                        asset_info = "_".join(asset_info_list[2:-1])
                        asset = asset_info.rstrip('0123456789')
                        group = "shotgun"
                    else:
                        asset = asset_info.rstrip('0123456789')
                        group = ""

                    if not os.path.isfile(xml):
                        return u"无效路径: " + xml
                    if not os.path.isfile(abc) and "/asb/" not in abc:
                        return u"无效路径: " + abc

                    if not self.dialog.d_assets.has_key(asset):
                        l_invalid.append(asset)
                    else:
                        self.dialog.hyperloop[asset] = self.dialog.d_assets[asset]
                        self.dialog.hyperloop[asset]['xml'] = xml
                        self.dialog.hyperloop[asset]['abc'] = abc
                        self.dialog.hyperloop[asset]['group'] = group


            if len(self.dialog.hyperloop) == 0:
                return u"xml文件中没有有效的资产"

            if len(l_invalid) > 0:
                return u"项目中不存在这些 prp, env 资产: " + ', '.join(l_invalid)
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

