# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Proceed rig publish files
#
############################################

import os
import traceback
import shutil
import pymel.core as pm
import maya.cmds as cmds

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"整理装配文件并拷贝到服务器。"
        self.description = u"待完善。"
        return


    def lock_weight(self):
        # lock skinCluster
        l_skins = pm.ls(type= 'skinCluster')
        for n in l_skins:
            n.setAttr('weightList', l=True)

        # lock blendShape
        blendShapes = pm.ls(type='blendShape')
        for n in blendShapes:
            n.setAttr('weight', lock=True)

        # lock other deformers
        deformers = pm.ls(type='weightGeometryFilter')
        for n in deformers:
            n.setAttr('weightList', lock=True)

        # lock joint
        self.l_locked_joints = []
        l_joints = pm.listRelatives('|master|rig', type='joint', ad=True)
        for n in l_joints:
            if n.hasAttr('liw'):
                if not n.getAttr('liw'):
                    n.setAttr('liw', True)
                    self.l_locked_joints.append(n)
        return


    def unlock_weight(self):
        # unlock skinCluster
        l_skins = pm.ls(type='skinCluster')
        for n in l_skins:
            n.setAttr('weightList', l=False)

        # unlock blendShape
        blendShapes = pm.ls(type='blendShape')
        for n in blendShapes:
            n.setAttr('weight', lock=False)

        # unlock other deformers
        deformers = pm.ls(type='weightGeometryFilter')
        for n in deformers:
            n.setAttr('weightList', lock=False)

        # unlock joint
        for n in self.l_locked_joints:
            n.setAttr('liw', False)

        return


    def lock_sacle_ctrls(self):
        if pm.objExists('global_ctrl'):
            n = pm.PyNode('global_ctrl')
            if n.hasAttr('globalScale'):
                pm.setAttr("global_ctrl.globalScale", lock=True)

        """ by guo.jianwei 2016.8.16
        for chr_ctrl in ["L_handFk_ctrl","R_handFk_ctrl","C_head_ctrl","L_footFk0_ctrl","R_footFk0_ctrl","L_legIk_ctrl","R_legIk_ctrl","L_armIk_ctrl","R_armIk_ctrl"]:
            if pm.objExists(chr_ctrl):
                try:
                    pm.transformLimits(chr_ctrl, sx=[-1, 1.3], esx=[False, True])
                    pm.transformLimits(chr_ctrl, sy=[-1, 1.3], esy=[False, True])
                    pm.transformLimits(chr_ctrl, sz=[-1, 1.3], esz=[False, True])
                except:
                    print 'Failed to lock', chr_ctrl
        """
        
        return

    def make_transform(self, name, parent=None):
        if not cmds.objExists(name):
            name = cmds.createNode('transform', name=name)

        parent_obj = cmds.listRelatives(name, p=True)
        if parent and cmds.objExists(parent):
            if parent_obj:
                if parent_obj[0] != parent:
                    cmds.parent(name, parent)
            else:
                cmds.parent(name, parent)

        return name

    def locator(self, name, r=1.0):
        """Create and return a cvLocator curve to be usually used in the guideSystem.
        """
        # create curve:
        locator = cmds.curve(n=name, d=1, p=[(0, 0, r), (0, 0, -r), (0, 0, 0), 
                                            (r, 0, 0), (-r, 0, 0), (0, 0, 0), 
                                            (0, r, 0), (0, -r, 0)] )

        return locator

    def add_misc_loc(self, obj=None):
        constr_objs = ["spine_M_spine_1_bind",
                       "root_ctrl",
                       "global_ctrl"]

        light_loc = "light_loc"

        # create misc group
        misc_grp = self.make_transform("misc", "master")

        # create light_loc
        if cmds.objExists(light_loc) == False:
            light_loc = self.locator("light_loc")
            light_loc_shape = cmds.listRelatives(light_loc, c=True)
            light_loc_shape = cmds.rename(light_loc_shape[0], "light_locShape")

            cmds.parent(light_loc, misc_grp)

        constr = cmds.listConnections(light_loc, s=True, d=False)
        if constr:
            return

        if obj:
            cmds.parentConstraint(obj, light_loc, weight=True, mo=True)
            return

        # parentConstraint for light_loc
        for item in constr_objs:
            if cmds.objExists(item):
                cmds.parentConstraint(item, light_loc, weight=True, mo=True)
                return

    def proceed(self):
        try:
            #lock = self.dialog.task['name'] != 'rigging_unlock'
            #if lock:
            #    self.lock_weight()
            ast_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])
            if ast_info['sg_asset_type'] == 'chr':
                self.add_misc_loc()

            pm.select("|master", r=True)
            assets=cmds.ls(type='container')
            if assets:
                pm.select(assets,add=True)

            pm.exportSelected( self.dialog.tank_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
            pm.select(cl=True)

            # Lock scale for chr
            if ast_info['sg_asset_type'] == 'chr':
                self.lock_sacle_ctrls()

            #if lock:
            #    self.unlock_weight()

            pm.saveFile(force=True)
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


