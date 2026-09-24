# -*- coding:utf-8 -*-

import xml.etree.ElementTree as ET
import os
import re

import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查引用的资产的数据是否完善。"
        self.description = u"检查引用的资产的xml数据是否完善。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        error_info = []
        for i in pm.ls(type="assemblyReference"):
            xml_dir = os.path.dirname(os.path.dirname(i.getAttr('definition')))
            asset_name = os.path.basename(i.getAttr('definition')).split('.')[0]
            asset_type = re.search('/asset/(\w+)/', i.getAttr('definition')).group(1)
            if asset_type in ['asb', 'flg']:
                continue
            xml_path = os.path.join(xml_dir, 'scene_graph_xml/{}.xml'.format(asset_name))
            if not os.path.exists(xml_path):
                error_info.append(asset_name)
                continue
            xml_tree = ET.parse(xml_path)
            xml_root = xml_tree.getroot()
            hi_instance = xml_root.find(".//instance[@name='hi']")
            bounds = hi_instance.find("bounds")
            if bounds is None:
                error_info.append(asset_name)
                continue
            if not bounds.get('maxx'):
                error_info.append(asset_name)
                continue

        if error_info:
            return u'这些资产的xml信息不全，需要重新发布\n{}'.format('\n'.join(list(set(error_info))))

        return ''


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




