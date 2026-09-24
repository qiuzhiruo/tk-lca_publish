# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: Guo JianWei
#
# Date: 2016.07
#
# Description: Export facial model abc for use in SRF and CFX
#
############################################

import os
import sys
import traceback
import hashlib
from xml.dom.minidom import Document
import pymel.core as pm
import maya.api.OpenMaya as om
import maya.cmds as cmds


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出含张嘴、睁眼等表情pose序列的abc文件。"
        self.description = u"导出含张嘴、睁眼、爪子展开(需含spread属性)共三帧动画的abc文件。"
        return

    def export_facial_frame_abc(self):
        mouth_up_value = 1
        mouth_dn_value = -0.5


        mouth_up_ctrls = ["mouth_L_up_1_ctrl","mouth_R_up_1_ctrl","mouth_R_up_2_ctrl","mouth_M_up_1_ctrl","mouth_L_up_2_ctrl"]
        mouth_dn_ctrls = ["mouth_L_dn_2_ctrl", "mouth_L_dn_1_ctrl", "mouth_M_dn_1_ctrl", "mouth_R_dn_1_ctrl", "mouth_R_dn_2_ctrl"]



        eye_ctrls = cmds.ls("*eyelid_L_up_all_ctrl",
                          "*eyelid_R_up_all_ctrl",
                          "*eyelid_L_dn_all_ctrl",
                          "*eyelid_R_dn_all_ctrl",
                          "*L_upEyelid_ctrl",
                          "*L_loEyelid_ctrl",
                          "*R_upEyelid_ctrl",
                          "*R_loEyelid_ctrl")

        finger_ctrls = cmds.ls("*leg*_L_setting_ctrl",
                             "*leg*_R_setting_ctrl",
                             "*arm*_L_setting_ctrl",
                             "*arm*_R_setting_ctrl")

        mouth_ctrls = cmds.ls("*jaw_M_openMouth_rotate_ctrl",
                            "*jaw_M_openMouth_ctrl",
                            "*jaw_M_open_ctrl",
                            "*mouth_open_ctrl",
                            "*lowJaw_ctrl",
                              "*jaw_M_ctrl")

        # 1. set key-----------------------------
        # set eye controls
        for item in eye_ctrls:
            neg = 1
            if item.count("_dn_") or item.count("_lo"):
                neg = -1 * neg

            if pm.objExists(item):
                pm.setKeyframe(item, at="ty", v=0, t=1)
                pm.setKeyframe(item, at="ty", v=0.5 * neg, t=2)
                pm.setKeyframe(item, at="ty", v=1.0 * neg, t=3)
                pm.setKeyframe(item, at="ty", v=0 * neg, t=4)

        for item in finger_ctrls:
            if pm.objExists("%s.spread" % item):
                pm.setKeyframe(item, at="spread", v=0, t=9)
                pm.setKeyframe(item, at="spread", v=5, t=10)
                pm.setKeyframe(item, at="spread", v=10, t=11)
                pm.setKeyframe(item, at="spread", v=0, t=12)

        # set mouth control
        for item in mouth_ctrls:
            if pm.objExists(item):
                pm.setKeyframe(item, at="rx", v=0, t=5)
                pm.setKeyframe(item, at="rx", v=10, t=6)
                pm.setKeyframe(item, at="rx", v=30, t=7)
                pm.setKeyframe(item, at="rx", v=0, t=8)

        for item in mouth_up_ctrls:
            if pm.objExists(item):
                pm.setKeyframe(item, at="ty", v=0, t=5)
                pm.setKeyframe(item, at="ty", v=mouth_up_value, t=6)
                pm.setKeyframe(item, at="ty", v=mouth_up_value, t=7)
                pm.setKeyframe(item, at="ty", v=0, t=8)

        for item in mouth_dn_ctrls:
            if pm.objExists(item):
                pm.setKeyframe(item, at="ty", v=0, t=5)
                pm.setKeyframe(item, at="ty", v=mouth_dn_value, t=6)
                pm.setKeyframe(item, at="ty", v=mouth_dn_value, t=7)
                pm.setKeyframe(item, at="ty", v=0, t=8)



        # 2. export facial abc-------------------
        # load plugin
        if pm.pluginInfo("AbcExport", q=1, l=1) == False:
            pm.loadPlugin("AbcExport")

        for asset_name in self.dialog.d_assets_info.keys():
            version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
            # root = self.dialog.d_assets_info[asset_name]['node']
            # node_name = self.dialog.d_assets_info[asset_name]['node_name']

        # -----------------------------export hi abc
        obj_path = "|master|poly|hi"
        if cmds.objExists(obj_path):
            abc_path = '%s/scene_graph_xml/%s.abc' % (
                version_dir,  obj_path.split('|')[-1])

            obj_child = cmds.listRelatives(obj_path, c=True, fullPath=True)
            if obj_child:
                # Create dirs
                if not os.path.isdir(version_dir + '/scene_graph_xml'):
                    os.makedirs(version_dir + '/scene_graph_xml')

                obj_all = " -root ".join(obj_child)
                pm.AbcExport(
                    j="-frameRange 1 12 -uvWrite -dataFormat ogawa -root %s -file %s" % (obj_all, abc_path))

        # ----------------------------export shape abc
        obj_path = "|master|shape"
        if cmds.objExists(obj_path):
            abc_path = '%s/scene_graph_xml/%s.abc' % (
                version_dir,  obj_path.split('|')[-1])

            obj_child = cmds.listRelatives(obj_path, c=True, fullPath=True)
            if obj_child:
                # Create dirs
                if not os.path.isdir(version_dir + '/scene_graph_xml'):
                    os.makedirs(version_dir + '/scene_graph_xml')

                obj_all = " -root ".join(obj_child)
                pm.AbcExport(
                    j="-frameRange 1 12 -uvWrite -dataFormat ogawa -root %s -file %s" % (obj_all, abc_path))

        # 3. delete all animCurves-----------------
        # get eye_ctrls
        try:
            mg_anim_nodes = cmds.ls("MG_PoseAnim_*")
            cmds.delete(mg_anim_nodes)
        except:
            pass

        unuse_nodes = []
        for item in eye_ctrls:
            if cmds.objExists(item):
                anim_node = pm.listConnections("%s.ty" % item,
                                               s=True,
                                               d=False,
                                               type="animCurveTL")
                unuse_nodes.extend(anim_node)

        # get finger_ctrls
        for item in finger_ctrls:
            if cmds.objExists("%s.spread" % item):
                anim_node = pm.listConnections("%s.spread" % item,
                                               s=True,
                                               d=False,
                                               type="animCurveTU")
                unuse_nodes.extend(anim_node)

        # get mouth_ctrl
        for item in mouth_ctrls:
            if cmds.objExists(item):
                anim_node = pm.listConnections("%s.rx" % item,
                                               s=True,
                                               d=False,
                                               type="animCurveTA")
                unuse_nodes.extend(anim_node)


        # get mouth_ctrl
        for item in mouth_up_ctrls:
            if cmds.objExists(item):
                anim_node = pm.listConnections("%s.ty" % item,
                                               s=True,
                                               d=False,
                                               type="animCurveTL")
                unuse_nodes.extend(anim_node)


        for item in mouth_dn_ctrls:
            if cmds.objExists(item):
                anim_node = pm.listConnections("%s.ty" % item,
                                               s=True,
                                               d=False,
                                               type="animCurveTL")
                unuse_nodes.extend(anim_node)


        # delete all nodes
        if unuse_nodes:
            pm.delete(unuse_nodes)

        # write asset fur info
        try:
            pro_name = self.dialog.project['name']
            asset_name = self.dialog.entity["name"]

            self.write_asset_info(pro_name, asset_name)

        except Exception, e:
            raise e


    def write_asset_info(self, pro_name, asset_name):
        # lctools_env = os.getenv('LCTOOLSET', '/mnt/utility/toolset')
        # # lctools_env="/mnt/work/home/wangbin/git_repo/lcatools"
        # sys.path.append(lctools_env + '/lib/production')

        import production.write_trash_cfx_rig as write_trash_cfx_rig
        reload(write_trash_cfx_rig)

        import production.write_trash_cfx_rig.writetrash as ww

        # pro_name="cat"
        # asset_name="nihaozhesizheshiceshi"
        ww.write_asseet_for_gen_fur(pro_name, asset_name)

    def proceed(self):
        try:
            self.export_facial_frame_abc()
            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
