# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.01
#
# Description: 
#
############################################

import traceback
from xml.etree import ElementTree
import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查Rig用的模型是否是released版本。"
        self.description = u"Released模型才可以被Rig和Srf使用。"
        self.auto_fix = False
        self.duty = u"项目管理。"
        return


    def get_trans(self, root):
        l_nodes = pm.listRelatives(root, type='transform')
        for node in l_nodes:
            if node.type() == 'transform':
                self.l_rig_trans.append(node.fullPath())
                self.get_trans(node)
        return


    def run_check(self):

        try:
            self.trans_match = False
            l_attrs = pm.listAttr('|master')
            if not ('modVersion' in l_attrs and 'modPath' in l_attrs):
                return u"没有找到 Mod Version 和 Mod Path 属性，无法对比模型层级。"

            mod_version = pm.getAttr('|master.modVersion')
            mod_path = pm.getAttr('|master.modPath')
            tokens = mod_path.split('/')
            if tokens[-1] != self.dialog.entity['name'] + '.ma':
                return u"使用的模型文件不是 " + self.dialog.entity['name'] + '.ma'

            version_name = tokens[-2]
            v_info = self.dialog.sg.find_one('Version', [['code', 'is', version_name]], ['sg_status_list'] )
            print v_info

            if v_info['sg_status_list'] != 'rels':
                return u"装配使用的模型版本: " + version_name + u" 还没有被通过, 状态不是\"rels(released)\"而是\"" + v_info['sg_status_list'] + u"\"。"
            
            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        "Auto Fix"
        return ""


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


