# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2018.01
#
# Description: 
#
############################################

import os
import traceback
import pickle
import pymel.core as pm
import maya.mel as mel

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录各 joint 在 body geo 上的权重"
        self.description = u"记录各 joint 在 body geo 上的权重。保存到版本文件夹下的 joint_weight.pkl 文件"
        return

    def proceed(self):
        try:
            mesh = "body_geo"
            if self.dialog.asset_type == 'chr' and pm.objExists(mesh):
                skinCluster = mel.eval('findRelatedSkinCluster '+mesh)
                if skinCluster == '':
                    return ""
                bind_jnts = pm.skinCluster(skinCluster, query=True, inf=True)
                d_vtx_joint_map = {}

                for i in range(pm.polyEvaluate(mesh, v=True)):
                    vtx = '%s.vtx[%s]' % (mesh, i)
                    skin_value_list = pm.skinPercent(skinCluster, vtx, query=True,value=True)
                    max_value_index = skin_value_list.index(max(skin_value_list))
                    jnt = bind_jnts[max_value_index].nodeName()
                    d_vtx_joint_map[vtx] = jnt

                f = open( self.dialog.version_dir + '/joint_weight.pkl', 'w')
                pickle.dump(d_vtx_joint_map, f)
                f.close()

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

