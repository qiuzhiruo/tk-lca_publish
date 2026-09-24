# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.05
#
# Description: 
#
############################################
import os
import traceback
import shutil
import pymel.core as pm
from sgtk.platform.qt import QtGui
import maya.cmds as cmds
import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om
import sys

import assetsystem_sgl
root_path = os.path.dirname(assetsystem_sgl.__file__)
#root_path = os.path.dirname(assetsystem_sgl.__file__)
root_path ='D:\\program\\git\\lca_rig\\assetsystem_sgl'
rig_mod_Path = root_path + "\\tools\\mod\\rig_mod"
if rig_mod_Path not in sys.path:
    sys.path.insert(0, rig_mod_Path)

import shotgun_rig_mod
reload(shotgun_rig_mod)
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出模型权重,rig_guides,rig_mod"
        self.description = u"导出模型权重,rig_guides,rig_mod"
        return

    def proceed(self):
        #print self.dialog.project['name'].upper()
        try:
            filename = self.dialog.tank_file
            shotgun_rig_mod.do_export(filename)
            asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type', 'sg_manual_lod'] )
            self.dialog.d_assets_info[self.dialog.entity['name']] = {'node':pm.PyNode('|master'),
                                                                     'node_name':'master',
                                                                     'parent':None,
                                                                     'asset':self.dialog.entity,
                                                                     'task':self.dialog.task,
                                                                     'type':asset['sg_asset_type'],
                                                                     'lod':asset['sg_manual_lod'],
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

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description