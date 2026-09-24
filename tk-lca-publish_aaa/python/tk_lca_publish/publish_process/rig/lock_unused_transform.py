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
from assetsystem_sgl.tools.common.publish.ls_nurbsCurve_ctrl import ref_all_nurbsCurve
from assetsystem_sgl.tools.common.publish.set_scene import lock_all_transform, set_AllInfinity_skinBlendWeight_to_Zero, \
    unlock_bakeAttrs, lock_all_unused_custom_attribute_on_dagnodes, hide_RBF_sphere, display_joint, \
    lock_allJoint_orient, \
    display_allGeo_shape, display_shapes, lock_deformers_weight
from sgtk.platform.qt import QtGui
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.cmds as mc


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"锁定所有不给动画使用的transform节点,将无关节点设置为不显示。"
        self.description = u"所有命名不规范的控制器以及group的transform属性会被锁定。follicle，locator,joint等等物体将不显示。锁skinCluster、BlendShape、Joint和自动创建light_loc定位给灯光。"
        return

    def lock_weight(self):
        # lock skinCluster
        l_skins = pm.ls(type='skinCluster')
        for n in l_skins:
            n.setAttr('weightList', l=True)

        # lock blendShape
        blendShapes = pm.ls(type='blendShape')
        for n in blendShapes:
            n.setAttr('weight', lock=True)
            try:
                n.setAttr('midLayerParent', lock=True)
            except:
                pass

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
                                             (0, r, 0), (0, -r, 0)])

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


    # Modified by Sheng Liao on 2021/11/24 -----------------------------------------------------------------------------

    # @staticmethod
    # def check_connect_blend(ctrl_name):
    #     breath_ctrl_node = pm.PyNode(ctrl_name)
    #     dri_ani_curves = breath_ctrl_node.outputs(type='animCurve')
    #     all_bs_nodes = []
    #     for dri_ani_curve in dri_ani_curves:
    #         bs_nodes = dri_ani_curve.outputs(type='blendShape')
    #         if not bs_nodes:
    #             continue
    #         all_bs_nodes.extend(bs_nodes)
    #     # lock ?
    #     if not all_bs_nodes:
    #         try:
    #             # lock attr
    #             cmds.setAttr('{}.breath_up'.format(ctrl_name), lock=True)
    #             cmds.setAttr('{}.breath_dn'.format(ctrl_name), lock=True)
    #         except:
    #             pass
    #
    # def lock_breath_ctrl_attr(self):
    #     spine_ctrl = "spine_M_3_ik_ctrl"
    #     breath_ctrl = 'body_M_setting_ctrl'
    #
    #     if not cmds.objExists(breath_ctrl) and not cmds.objExists(spine_ctrl):
    #         return
    #     # check connect blend spine_ctrl
    #     if cmds.objExists(spine_ctrl):
    #         self.check_connect_blend(ctrl_name=spine_ctrl)
    #     # check connect blend breath_ctrl
    #     if cmds.objExists(breath_ctrl):
    #         self.check_connect_blend(ctrl_name=breath_ctrl)
    #     return True

    def check_breathattr_connected_in_DAG(self, root_plug):
        res = False

        dag_it = om.MItDependencyGraph(root_plug,
                                       om.MItDependencyGraph.kDownstream,
                                       om.MItDependencyGraph.kNodeLevel,
                                       om.MItDependencyGraph.kDepthFirst)

        dag_it.reset()

        while not dag_it.isDone():
            current_item = dag_it.currentItem()

            if current_item.hasFn(om.MFn.kBlendShape) or \
                    current_item.hasFn(om.MFn.kAnimCurveTimeToAngular) or \
                    current_item.hasFn(om.MFn.kAnimCurveTimeToDistance) or \
                    current_item.hasFn(om.MFn.kAnimCurveTimeToTime) or \
                    current_item.hasFn(om.MFn.kAnimCurveTimeToUnitless) or \
                    current_item.hasFn(om.MFn.kAnimCurveUnitlessToAngular) or \
                    current_item.hasFn(om.MFn.kAnimCurveUnitlessToDistance) or \
                    current_item.hasFn(om.MFn.kAnimCurveUnitlessToTime) or \
                    current_item.hasFn(om.MFn.kAnimCurveUnitlessToUnitless):
                target_node_fn = om.MFnDependencyNode(current_item)

                plug_path = om.MPlugArray()
                dag_it.getPlugPath(plug_path)
                plug_count = plug_path.length()
                breath_attr = plug_path[plug_count - 1].name()

                # print 'The breath attribute "%s" is connected to a blendShape or ' \
                #       'animCurve node "%s".' % (breath_attr, target_node_fn.name())
                res = True
                break

            dag_it.next()

        return res

    def lock_breath_attrs(self):
        breath_ctrl = ''

        if cmds.objExists('body_M_setting_ctrl'):
            breath_ctrl = 'body_M_setting_ctrl'
        # The third-level characters do not have the "body_M_setting_ctrl" controller,
        # but they should have the "spine_M_3_ik_ctrl" joint.
        elif cmds.objExists('spine_M_3_ik_ctrl'):
            breath_ctrl = 'spine_M_3_ik_ctrl'
        # Neither do non-living characters/props have the "body_M_setting_ctrl" controller,
        # nor do they have the "spine_M_3_ik_ctrl" joint.
        else:
            # Get the rigging file name.
            file_path = cmds.file(query=True, sceneName=True)
            file_name = os.path.basename(file_path)
            cmds.warning('The rigging file "%s" does not have the "body_M_setting_ctrl" controller or '
                         'the "spine_M_3_ik_ctrl" joint!' % file_name)
            return

        # We assume that the "body_M_setting_ctrl" controller has the attributes "Breath Up" and "Breath Dn".
        if not cmds.objExists(breath_ctrl + ".breath_up"):
            cmds.error('There should be a "breath_up" attribute on the "body_M_setting_ctrl" controller!')
        if not cmds.objExists(breath_ctrl + ".breath_dn"):
            cmds.error('There should be a "breath_dn" attribute on the "body_M_setting_ctrl" controller!')

        breath_ctrl_node = om.MObject()

        selection = om.MSelectionList()
        om.MGlobal.getSelectionListByName(breath_ctrl, selection)
        selection.getDependNode(0, breath_ctrl_node)

        breath_ctrl_nodeFn = om.MFnDependencyNode(breath_ctrl_node)
        breath_up_plug = breath_ctrl_nodeFn.findPlug("breath_up")
        breath_dn_plug = breath_ctrl_nodeFn.findPlug("breath_dn")

        print ''
        print '========================================================================================================='
        print '                                     Lock Attributes for the Breath Controller'
        print '========================================================================================================='

        # Unlock the breath controller node if it was locked for some reason, or we cannot lock/unlock its attributes.
        cmds.lockNode(breath_ctrl, lock=False)

        if not self.check_breathattr_connected_in_DAG(breath_up_plug):
            print 'Lock the attribute "%s" because it is not connected to any blendShape or ' \
                  'animCurve node.' % breath_up_plug.name()
            cmds.setAttr(breath_up_plug.name(), lock=True)
        else:
            print 'The attribute "%s" should NOT be locked. Unlock it.' % breath_up_plug.name()
            # We unlock the "Breath Up" attribute here in case it was locked accidentally.
            cmds.setAttr(breath_up_plug.name(), lock=False)

        if not self.check_breathattr_connected_in_DAG(breath_dn_plug):
            print 'Lock the attribute "%s" because it is not connected to any blendShape or ' \
                  'animCurve node.' % breath_dn_plug.name()
            cmds.setAttr(breath_dn_plug.name(), lock=True)
        else:
            print 'The attribute "%s" should NOT be locked. Unlock it.' % breath_dn_plug.name()
            # We unlock the "Breath Dn" attribute here in case it was locked accidentally.
            cmds.setAttr(breath_dn_plug.name(), lock=False)

    # ----------------------------------------------------------------------------- Modified by Sheng Liao on 2021/11/24

    def proceed(self):
        # print self.dialog.project['name'].upper()
        if not self.dialog.project['name'].upper() == 'GOD':
            try:
                lock = self.dialog.task['name'] != 'rigging_unlock'
                if lock:
                    self.lock_weight()

                ast_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])
                if ast_info['sg_asset_type'] == 'chr':
                    self.add_misc_loc()
                    if cmds.objExists("anim_guides_grp"):
                        cmds.delete("anim_guides_grp")

                lock_deformers_weight(1)
                display_shapes(0, 'locator')
                display_shapes(0, 'lattice')
                display_shapes(0, 'clusterHandle')
                display_shapes(0, 'follicle')
                display_allGeo_shape(v=0)
                lock_allJoint_orient(1)
                display_joint(1)
                ref_all_nurbsCurve(1)
                hide_RBF_sphere(0)
                lock_all_unused_custom_attribute_on_dagnodes(1)
                unlock_bakeAttrs()
                set_AllInfinity_skinBlendWeight_to_Zero()

                snake_list = mc.ls("snake*")
                if snake_list or mc.objExists("master.asm_rigging"):
                    lock_all_transform(lock=1,
                                       removeStrFilter=['_ctrl_con', '_ctrl_drv', '_pri_ctrl', '_sec_ctrl', '_SN',
                                                        '_PH', 'Gimbal_ctrl', 'persp', 'side', 'front', 'top'])
                else:
                    lock_all_transform(lock=1,
                                       removeStrFilter=['_pri_ctrl', '_sec_ctrl', '_SN', '_PH', 'Gimbal_ctrl', 'persp',
                                                        'side', 'front', 'top'])

                unusedattrs = ["arm_L_wrist_ik_ctrl.user_up_stretch", "arm_L_wrist_ik_ctrl.user_low_stretch",
                               "leg_L_ankle_ik_ctrl.user_low_stretch", "leg_L_ankle_ik_ctrl.user_up_stretch",
                               "leg_R_ankle_ik_ctrl.user_low_stretch", "leg_R_ankle_ik_ctrl.user_up_stretch",
                               "arm_R_wrist_ik_ctrl.user_low_stretch", "arm_R_wrist_ik_ctrl.user_up_stretch",
                               "arm_L_wrist_ik_ctrl.user_low_stretch", "arm_L_wrist_ik_ctrl.user_up_stretch"]
                for tattr in unusedattrs:
                    try:
                        mc.setAttr(tattr, e=1, l=0)
                    except:
                        pass

                # lock_breath_ctrl_attr
                # Modified by Sheng Liao on 2021/09/03 ---------------------------------------
                # self.lock_breath_ctrl_attr()
                self.lock_breath_attrs()
                # --------------------------------------- Modified by Sheng Liao on 2021/09/03

                # Lock scale for chr
                # if ast_info['sg_asset_type'] == 'chr':
                #     self.lock_sacle_ctrls()

                # if lock:
                #     self.unlock_weight()
                return ""
            except:
                return traceback.format_exc()
        else:
            return ""

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
