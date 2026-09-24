# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Ying jie
#
# Date: 2014.04
#
# Description: Check shtogun data
#
############################################

import traceback

import os
import re
from sgtk.platform.qt import QtCore, QtGui

def get_lgt_shot_maker_node():
    import NodegraphAPI as ngapi
    all_grp_nodes = ngapi.GetAllNodesByType('Group')
    for gn in all_grp_nodes:
        if gn.getName() == 'LgtShotMaker_Lc':
            return gn

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的Katana文件(*.katana)的路径和命名。"
        self.description = u"Katana 文件包含两个xml文件，会随同一起publish"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def check_path(self, path, key):
        p = re.compile("[\w\.]*$")
        tokens = path.replace(":", "\\").replace("/", "\\").split("\\")
        for token in tokens:
            if not p.match(token):
                return key + u" 各级文件夹需要由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成:\n  " + path

        return ''


    def run_check(self):

        try:
            st_node = get_lgt_shot_maker_node()
            if not st_node:
                return u'找不到 LgtShotMaker_Lc 节点'

            shot = st_node.getParameter('user.shot').getValue(0)
            if not shot or shot != self.dialog.entity['name']:
                return u'ShotMaker节点的shot参数与publish 镜头不符'
            return ''
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


