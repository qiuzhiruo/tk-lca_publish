# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description: 
#
############################################

import traceback

import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产的 master 节点。"
        self.description = u"资产的最上层组为master。如果存在，将这个节点记录到 self.dialog.d_assets_info 中。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            self.dialog.d_assets_info = {}
            
            if not pm.objExists("|facial_model_grp"):
                return u"没有找到最高层的 |facial_model_grp 组。"

            # to mark which group needs standard model checks
            asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'] )
            self.dialog.d_assets_info[self.dialog.entity['name']] = {'node':pm.PyNode('|facial_model_grp'),
                                                                     'node_name':'|facial_model_grp',
                                                                     'parent':None,
                                                                     'asset':self.dialog.entity,
                                                                     'task':self.dialog.task,
                                                                     'type':asset['sg_asset_type'],
                                                                     'publish_dir':self.dialog.publish_root,
                                                                     'version_name':self.dialog.version_name,
                                                                     'version_dir':self.dialog.publish_root + '/' + self.dialog.version_name,
                                                                     'tank_file': self.dialog.publish_root + '/' + self.dialog.version_name + '/' + self.dialog.entity['name'] + '.ma',
                                                                     'translation':(0.0, 0.0, 0.0),
                                                                     'rotation':(0.0, 0.0, 0.0),
                                                                     'v_info':None}

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


