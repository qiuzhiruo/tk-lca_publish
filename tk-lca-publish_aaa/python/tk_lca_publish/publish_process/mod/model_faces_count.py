# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description: 
#
############################################

import os
import traceback
import hashlib
from xml.dom.minidom import Document
import pymel.core as pm
import maya.api.OpenMaya as om
import json
from proc.function_running_time import record_time



# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录文件的hi组总面数信息。"
        self.description = u"hi组的总面数信息。"
        return

    def hi_group_mesh_count(self,root):
        list_mesh=pm.listRelatives(root.fullPath()+'|poly|hi',ad=True,type='mesh')
        if not list_mesh:
            return {'triangle': 0, 'uvcoord': 0, 'edge': 0, 'vertex': 0, 'face': 0}

        pm.select(list_mesh)
        face_num = pm.polyEvaluate(v=True, f=True, e=True, uv=True, t=True)

        return face_num

    @record_time(__file__)
    def proceed(self):
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                faces_count = version_dir + '/faces_count.json'
                root = self.dialog.d_assets_info[asset_name]['node']
                face_dict= self.hi_group_mesh_count(root)
                with open(faces_count, 'w') as f:
                    json.dump(face_dict, f)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


