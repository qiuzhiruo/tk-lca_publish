# -*- coding:utf-8 -*-
############################################
# Author: chen gang
############################################

import traceback
import maya.cmds as cmds
import os
import string
import xml.etree.ElementTree as ET



def get_root(file_path):
    if not os.path.isfile(file_path):
        print 'file_path: %s' % file_path
        raise ValueError, 'Warning: file does not exist'
    xml_tree = ET.parse(file_path)
    xml_root = xml_tree.getroot()
    return xml_root


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查动画da镜头里,rig是否删除了控制器"
        self.description = u"检查动画da镜头里,rig是否删除了控制器"
        self.auto_fix = False
        self.duty = u"艺术家本人 或 TD。"
        return

    def check_skeleton_chain(self):
        asset_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])


    def run_check(self):
        try:
            fields = ['step','id', 'code', 'sg_asset_type','sg_status_list','content']
            animation_tasks = self.dialog.sg.find('Task',[['entity.Shot.assets', 'in', self.dialog.entity],
                                              ['step', 'name_is', 'ani'],
                                              ['content', 'is', 'animation'],
                                              ['sg_status_list', 'is_not', 'omt'],
                                              {'filter_operator': 'any','filters': [['sg_status_list', 'is', 'da']],}],fields,)
            asset_name = self.dialog.entity['name'].lower()
            version_dir = self.dialog.d_assets_info[asset_name]['version_dir'].lower()
            if animation_tasks:
                current_num = version_dir.split(".v")[-1]
                if current_num.isdigit():
                    if int(current_num) > 1 :
                        num = int(current_num) - 1
                        previous_num = string.zfill(num, 3)
                        previous_version_dir = version_dir.replace(current_num, previous_num)
                        previous_version_file = "%s/rig_info.xml" % previous_version_dir
                        previous_ctrls = []
                        if os.path.isfile(previous_version_file):
                            previous_xml_root = get_root(previous_version_file)
                            control_node = previous_xml_root.findall('controlInfo')
                            if control_node:
                                nodes = control_node[0].getchildren()
                                if nodes:
                                    for node in nodes:
                                        ctrl = node.attrib["name"]
                                        previous_ctrls.append(ctrl)
                                all_ctrls = cmds.ls("*_ctrl")
                                all_ctrls = set(all_ctrls)
                                previous_ctrls = set(previous_ctrls)
                                old = list(previous_ctrls.difference(all_ctrls))
                                if old:
                                    cmds.confirmDialog( title='file check', message=u"动画文件存在已经da的镜头不允许删除控制器\n和上一版比,已删除{}个控制器 请检查rig文件控制器是否改名\n查看脚本编辑器查看删除的控制器".format(len(old)), button=[u'我知道了'], defaultButton='Yes',)
                                    return u"和上一版比，已删除控制器：{0} ;".format(old)
                                else:
                                    return ""

            else:
                return ""
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


