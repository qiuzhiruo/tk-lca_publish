# -*- coding:utf-8 -*-

#
# Copyright (c) 2023 Light Chaser Animation Studios. All Rights Reserved.
#
# File Name: check_muggle_restrictions.py
# Author: Sheng (Raymond) Liao
# Date: June 2023
#

"""
A module to check if the rig contains the known restrictions of the Muggle RigX acceleration framework
such as nodes or node attributes that are not implemented or not fully supported.
This module also does auto-fixings such as unlocking nodes and cleaning trivial nodes unimplemented in the framework.
"""

import re
import traceback

import maya.cmds as cmds

g_zero_threshold = 1e-5

lock_transattr_lambda = lambda node, lock: [cmds.setAttr('{}.{}{}'.format(node, attr, axis), lock=lock)
                                            for attr in 'trs'
                                                for axis in 'xyz']

list_connected_transplug_lambda = lambda node: [nodelist[0] for nodelist in
                                                [cmds.listConnections('{}.{}{}'.format(node, attr, axis))
                                                    for attr in 'trs'
                                                        for axis in 'xyz']
                                                if None != nodelist] +\
                                               [nodelist[0] for nodelist in
                                                [cmds.listConnections('{}.{}'.format(node, attr))
                                                    for attr in ['translate', 'rotate', 'scale']]
                                                    if None != nodelist]
class traversalDirEnum(object):
    eDownStream = 0
    eUpStream = 1

class plugTypeEnum(object):
    input = 0
    output = 1

class restrictLvEnum(object):
    warning = 0,
    fail = 1

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'Muggle绑定加速框架节点限制检查'
        self.description = u'检查是否有Muggle绑定加速框架所限制的节点条件出现。'
        self.auto_fix = False
        self.duty = u'艺术家本人/TD'
        return

    def run_check(self):

        try:
            # We do not do this check for facial, layout or prop rigging assets.
            current_scene_name = cmds.file(query=True, sceneName=True)  # e.g. W:/projects/can/asset/prp/...

            # Note that in some cases we will retrieve an empty string instead of the current file path.
            if len(current_scene_name) > 0:
                # asset_type = current_scene_name.split('/')[4]
                # if 'prp' == asset_type:
                #     cmds.warning(u'[Muggle节点限制检查] 不检查"prp"（道具）绑定资产。')
                #     return ''
                # elif 'chr' == asset_type:
                #     if 'rigging_facial' in current_scene_name:
                #         cmds.warning(u'[Muggle节点限制检查] 不检查"rigging_facial"（面部）绑定资产。')
                #         return ''
                #     if 'rigging_layout' in current_scene_name:
                #         cmds.warning(u'[Muggle节点限制检查] 不检查"rigging_layout"（layout）绑定资产.')
                #         return ''
                if 'prp' in current_scene_name:
                    cmds.warning(u'[Muggle节点限制检查] 不检查"prp"（道具）绑定资产。')
                    return ''
                if 'rigging_facial' in current_scene_name:
                    cmds.warning(u'[Muggle节点限制检查] 不检查"rigging_facial"（面部）绑定资产。')
                    return ''
                if 'rigging_layout' in current_scene_name:
                    cmds.warning(u'[Muggle节点限制检查] 不检查"rigging_layout"（layout）绑定资产.')
                    return ''

            check_passed, feedback_info = self.check_muggle_restrictions()

            if not check_passed:
                feedback_info = u'[Muggle节点限制检查] 检查不通过，具体信息如下: \n' + feedback_info
                return feedback_info
            else:
                return ''
        except:
            return traceback.format_exc()

    def check_muggle_restrictions(self):
        # --------------------------------------------------------------------------------------------------------------
        # A dictionary to mark all the checking steps we must go through.
        # Dictionary format: {checking_function: (description, restrict_level, if_execute)}
        preprocessing_step_dict = {
            # Preprocessing Steps
            self.unlock_transform_nodes: (u'被锁的变换(transform)节点 #自动修正#', restrictLvEnum.fail, True),
            self.clean_trivial_nodes: (u'清理Muggle框架未实现的节点 #自动修正#', restrictLvEnum.fail, True),
            self.clean_quat2euler_nodes: (u'清理quatToEuler节点 #自动修正#', restrictLvEnum.fail, True),
            self.clean_tweak_vplist: (u'清理tweak节点的vlist和plist数组 #自动修正#', restrictLvEnum.fail, True),
            self.rectify_zeroscaled_crvs: (u'置1缩放值为0的曲线', restrictLvEnum.fail, True),
            self.rectify_polyEdge2Curve_nodes: (u'置1阶数为3的polyEdgeToCurve节点', restrictLvEnum.fail, True),

            # Checking Steps
            self.search_forbidden_nodes: (u'Muggle框架未实现的节点 #手动/酌情修正', restrictLvEnum.fail, True),
            self.search_unfrozen_meshtransforms: (u'未被冻结变换(transform)的网格节点 #脚本修正#', restrictLvEnum.fail, True),
            self.search_nonzero_rotaxes: (u'旋转轴不为零向量的变换（transform）及骨骼(joint)节点 #手动修正#', restrictLvEnum.fail, True),
            self.search_rigpass_hiding_meshes: (u'被Rig Pass隐藏的网格(mesh)节点 #自动修正#', restrictLvEnum.warning, False),
            self.search_standalone_joints: (u'不与控制器直接或间接相连的骨骼(joint)节点 #酌情修正#', restrictLvEnum.warning, True),
            self.search_invalid_constraints: (u'唯一的权重属性其值为0的约束(constraint)节点 #酌情修正#', restrictLvEnum.warning, True),
            self.search_invalid_skinclusters: (u'不符合限制条件的蒙皮(skinCluster)节点 #手动/酌情修正#', restrictLvEnum.warning, True),
            self.search_invalid_curveinfos: (u'输出数组有空元素的curveInfo节点 #酌情修正#', restrictLvEnum.warning, True),
            self.search_invalid_lcchainvolumes: (u'输入plugs没有连接的lcChainVolume节点 #手动修正#', restrictLvEnum.fail, False),
            self.search_invalid_iksolvers: (u'不符合限制条件的ikHandle节点 #手动修正#', restrictLvEnum.fail, True)
        }
        # --------------------------------------------------------------------------------------------------------------

        all_steps_passed = True
        feedback_info = ''

        existing_node_dict = self.create_existing_nodes_dictionary()

        for step in preprocessing_step_dict.keys():
            if preprocessing_step_dict[step][2]:
                res, step_info = step(existing_node_dict)
                if (restrictLvEnum.fail == preprocessing_step_dict[step][1]) and not res:
                    feedback_info += step_info
                    feedback_info += u'检查/流程项 "{}" 不通过.\n'.format(preprocessing_step_dict[step][0])
                    all_steps_passed = False

        return all_steps_passed, feedback_info

    # Preprocessing Steps ----------------------------------------------------------------------------------------------
    def unlock_transform_nodes(self, existing_node_dict, console_print=True):
        ''' Unlock all the transform nodes serving as groups.
        :param existing_node_dict: dictionary
                                   all nodes' names and the types they are of as the dictionary keys
        :return: bool, string
                 1) always True
                 2) the locked transform node names
        '''
        if 'transform' not in existing_node_dict:
            return True, ''

        step_info = ''
        locked_node_list = []

        # --------------------------------------------------------------------------------------------------------------
        # The attributes that don't count as Rig Passes
        keyword_filter_list = ['RBF']
        # --------------------------------------------------------------------------------------------------------------

        for transform_node in existing_node_dict['transform']:
            should_filter = False
            for keyword in keyword_filter_list:
                if keyword in transform_node:
                    should_filter = True
            if should_filter:
                continue

            if (cmds.lockNode(transform_node, query=True)[0]):
                locked_node_list.append(transform_node)
                cmds.lockNode(transform_node, lock=False)

        if len(locked_node_list) > 0:
            step_info += u'\n=============== 被锁的变换(transform)节点 #自动修正# ===============\n'
            step_info += u'以下transform节点被锁住（已自动解锁）: \n\n'

            for locked_node in locked_node_list:
                step_info += u'【{}】\n'.format(locked_node)

        step_info += '\n'
        if console_print and ('\n' != step_info):
            cmds.warning(step_info)

        return True, step_info

    def clean_trivial_nodes(self, existing_node_dict, console_print=True):
        ''' Delete nodes of types listed in this function directly because the Muggle framework does not
        implement them and the deletion will not cause substantial effects.

        Trivial Node Type List:
        [deleteUVSet] We will transfer UV sets from techRig files after the Muggle compilation.
        [polyTransfer] We will transfer UV sets from techRig files after the Muggle compilation.
        :return: bool, str
                 1) always to be True to indicate the success of the process
                 2) the names of the trivial nodes deleted
        '''

        step_info = ''
        found_trivial_node = False

        trivial_nodes_dict = {'deleteUVSet':[],
                              'polyTransfer':[]}

        for node_type in trivial_nodes_dict.keys():
            if node_type not in existing_node_dict:
                continue

            trivial_node_list = existing_node_dict[node_type]
            if len(trivial_node_list) > 0:
                found_trivial_node = True

            for trivial_node in trivial_node_list:
                trivial_nodes_dict[node_type].append(trivial_node)

        if found_trivial_node:
            step_info += u'\n=============== 清理Muggle框架未实现的节点 #自动修正# ===============\n'
            step_info += u'下列节点未在Muggle框架中实现且将其删除不会产生实质性影响，将被自动清理:\n\n'

            for node_type in trivial_nodes_dict.keys():
                if node_type not in existing_node_dict.keys():
                    continue

                step_info += '--- {} ---\n'.format(node_type)
                if ('deleteUVSet' == node_type) or ('polyTransfer' == node_type):
                    step_info += u'标注：经Muggle框架编译后网格的材质会丢失，故删除此类节点无实际影响。\n'
                    for trivial_node in existing_node_dict[node_type]:
                        step_info += u'【{}】\n'.format(trivial_node)

                        cmds.delete(trivial_node)

                step_info += '\n'

        step_info += '\n'
        if console_print and ('\n' != step_info):
            cmds.warning(step_info)

        return True, step_info

    def clean_quat2euler_nodes(self, existing_node_dict, console_print=True):
        ''' Bypass all the quatToEuler nodes in the rig file then delete them.
        The quatToEuler nodes in node chains will cause the following known controllers to be invalid:
            * jaw_M_open_ctrl
            * mouth_M_up_all_ctrl
            * mouth_M_dn_all_ctr
        :return: bool, string
                 1) always to be True to indicate the success of the process
                 2) the names of the quatToEuler nodes deleted
        '''
        cmds.loadPlugin('quatNodes')
        if 'quatToEuler' not in existing_node_dict:
            return True, ''

        step_info = ''
        invalid_node_list = []

        quat_node_list = existing_node_dict['quatToEuler']
        if len(quat_node_list) > 0:
            step_info += u'\n=============== 清理quatToEuler节点 #自动修正# ===============\n'
            step_info += u'标注: quatToEuler节点若出现在嘴和下颌rig处，会造成编译后的下列张嘴控制器失效，将被自动清理。\n'
            step_info += 'jaw_M_open_ctrl\nmouth_M_up_all_ctrl\nmouth_M_dn_all_ctrl\n\n'
            step_info += u'quatToEuler节点:\n'

        for quat_node in quat_node_list:
            step_info += u'【{}】\n'.format(quat_node)

            inputquat_inputplug_list = cmds.listConnections(quat_node + '.inputQuat',
                                                            source=True, destination=False, plugs=True)
            if None == inputquat_inputplug_list:
                continue
            inputquat_input = inputquat_inputplug_list[0].split('.')[0]

            outputRotate_outputplug_list = cmds.listConnections(quat_node + '.outputRotate',
                                                                source=False, destination=True, plugs=True)
            if None == outputRotate_outputplug_list:
                continue
            outputRotate_outputplug = outputRotate_outputplug_list[0]

            cmds.connectAttr(inputquat_input + '.outputRotate', outputRotate_outputplug, force=True)
            cmds.delete(quat_node)

        step_info += '\n'
        if console_print and ('\n' != step_info):
            cmds.warning(step_info)

        return True, step_info

    def clean_tweak_vplist(self, existing_node_dict, console_print=True):
        # --------------------------------------------------------------------------------------------------------------
        # If we should clean the data of "plist" of tweak nodes.
        b_cleanup_twkplist = False
        # --------------------------------------------------------------------------------------------------------------

        if 'tweak' not in existing_node_dict:
            return True, ''

        step_info = ''
        invalid_node_dict = {}

        twknode_list = existing_node_dict['tweak']
        b_vlist_allelem_zero = True
        b_plist_allelem_zero = True

        for twknode in twknode_list:
            info_str = ''
            b_vlist_allelem_zero = True
            b_plist_allelem_zero = True

            # Note that the "vlist" and "plist" should always be compound attributes,
            # so we set the keyword argument "multi" to be true.
            twknode_multiattr_list = cmds.listAttr(twknode, multi=True)
            twknode_vlistattr_list = []
            twknode_plistattr_list = []
            for twknode_multiattr in twknode_multiattr_list:
                if 'vlist' in twknode_multiattr:
                    twknode_vlistattr_list.append(twknode_multiattr)
                elif 'plist' in twknode_multiattr:
                    twknode_plistattr_list.append(twknode_multiattr)

            # We should get a set of vlist and another of plist here, e.g. {vlist[0], vlist[1]}; {plist[0], plist[1]}
            twknode_vlistattr_set = set(twknode_vlistattr_list)
            twknode_plistattr_set = set(twknode_plistattr_list)

            for twknode_vlistattr in twknode_vlistattr_set:
                # The sub-attributes can be "x/y/zVertex" or "x/y/zValue".
                if ('vertex' in twknode_vlistattr) and \
                        ('xV' not in twknode_vlistattr and
                         'yV' not in twknode_vlistattr and
                         'zV' not in twknode_vlistattr):
                    twknode_vlistattr_val_tup = cmds.getAttr(twknode + '.' + twknode_vlistattr)[0]
                    b_vlist_elem_zero = True
                    for twknode_vlistattr_val in twknode_vlistattr_val_tup:
                        if abs(twknode_vlistattr_val) > g_zero_threshold:
                            b_vlist_elem_zero = False
                            break

                    if not b_vlist_elem_zero:
                        b_vlist_allelem_zero = False

                        info_str += twknode_vlistattr.replace(twknode + '.', '')
                        info_str += ': ({:.3f}, {:.3f}, {:.3f})\n'.format(twknode_vlistattr_val_tup[0],
                                                                          twknode_vlistattr_val_tup[1],
                                                                          twknode_vlistattr_val_tup[2])
                        cmds.setAttr(twknode + '.' + twknode_vlistattr, 0, 0, 0)

            if not b_vlist_allelem_zero:
                info_str += '\n'

            if b_cleanup_twkplist:
                for twknode_plistattr in twknode_plistattr_set:
                    if ('controlPoints' in twknode_plistattr) and \
                            ('xV' not in twknode_plistattr and
                             'yV' not in twknode_plistattr and
                             'zV' not in twknode_plistattr):
                        twknode_plistattr_val_tup = cmds.getAttr(twknode + '.' + twknode_plistattr)[0]
                        b_plist_elem_zero = True
                        for twknode_plistattr_val in twknode_plistattr_val_tup:
                            if abs(twknode_plistattr_val) > g_zero_threshold:
                                b_plist_elem_zero = False
                                break

                        if not b_plist_elem_zero:
                            b_plist_allelem_zero = False

                            info_str += twknode_plistattr.replace(twknode + '.', '')
                            info_str += ': ({:.3f}, {:.3f}, {:.3f})\n'.format(twknode_plistattr_val_tup[0],
                                                                              twknode_plistattr_val_tup[1],
                                                                              twknode_plistattr_val_tup[2])
                            cmds.setAttr(twknode + '.' + twknode_plistattr, 0, 0, 0)

                if not b_plist_allelem_zero:
                    info_str += '\n'

            if (not b_vlist_allelem_zero) or (not b_plist_allelem_zero):
                invalid_node_dict[twknode] = info_str

        if (len(invalid_node_dict.keys()) > 0):
            step_info += u'\n=============== 清理tweak节点的vlist和plist数组 #自动修正 ===============\n'
            step_info += u'Muggle框架tweak节点没有包含vlist和plist的重载函数。\n\n'

            for twknode in invalid_node_dict.keys():
                step_info += u'【{}】\n'.format(twknode)
                step_info += invalid_node_dict[twknode]

        step_info += '\n'
        if console_print and ('\n' != step_info):
            cmds.warning(step_info)

        return True, step_info

    def rectify_zeroscaled_crvs(self, existing_node_dict, console_print=True):
        ''' Set to 1 the scale components of NURBS-curves' transformation nodes in the rig file if nearly 0.
        :return: bool, string
                 1) always to be True to indicate the success of the process
                 2) the names of the curves with zero scaling
        '''
        if 'nurbsCurve' not in existing_node_dict:
            return True, ''

        step_info = ''
        invalid_node_dict = {}

        nurbs_crv_list = existing_node_dict['nurbsCurve']
        for nurbs_crv in nurbs_crv_list:
            # nurbs_crv_trans = nurbs_crv.split('Shape')[0]
            nurbs_crv_trans_list = cmds.listRelatives(nurbs_crv, parent=True, type='transform')
            # The NURBS curve shape may not have a corresponding transform node.
            if None == nurbs_crv_trans_list:
                continue
            nurbs_crv_trans = nurbs_crv_trans_list[0]

            is_zero_scaled = False
            scale_values = cmds.getAttr(nurbs_crv_trans + '.scale')[0]

            scale_compo_list = ['x', 'y', 'z']
            for scale_compo in scale_compo_list:
                scale_attr = nurbs_crv_trans + ".s" + scale_compo
                scale_attr_val = cmds.getAttr(scale_attr)
                if abs(scale_attr_val) < g_zero_threshold:
                    is_zero_scaled = True
                    if cmds.getAttr(scale_attr, lock=True):
                        cmds.setAttr(scale_attr, lock=False)
                        cmds.setAttr(scale_attr, 1.0)
                        cmds.setAttr(scale_attr, lock=True)
                    else:
                        cmds.setAttr(scale_attr, 1.0)
                        continue

            if is_zero_scaled:
                invalid_node_dict[nurbs_crv] = u' 其缩放值为: {}\n'.format(scale_values)

        if (len(invalid_node_dict.keys()) > 0):
            step_info += u'\n=============== 置1缩放值为0的曲线 #自动修正 ===============\n'
            step_info += u'缩放值为0的曲线会造成编译后的Muggle rig网格丢失。\n\n'

            for nurbs_crv in invalid_node_dict.keys():
                step_info += (u'【{}】'.format(nurbs_crv) + invalid_node_dict[nurbs_crv])

        step_info += '\n'
        if console_print and ('\n' != step_info):
            cmds.warning(step_info)

        return True, step_info

    def rectify_polyEdge2Curve_nodes(self, existing_node_dict, console_print=True):
        ''' Forcefully change the degree of all the polyEdgeToCurve nodes to 1,
        because the algorithm from the corresponding overloaded function of the Muggle framework
        that outputs degree 3 NURBS curve produces wrong values.
        :return: bool, string
                 1) always to be True to indicate the success of the process
                 2) the names of the polyEdgeToCurve nodes with degree of 3
        '''

        if 'polyEdgeToCurve' not in existing_node_dict:
            return True, ''

        step_info = ''
        invalid_node_list = []

        d3_polyEdge2Curve_node_list = [pe2c_node for pe2c_node in existing_node_dict['polyEdgeToCurve']
                                       if (3 == cmds.getAttr(pe2c_node + '.degree'))]
        for d3_polyEdge2Curve_node in d3_polyEdge2Curve_node_list:
            invalid_node_list.append(d3_polyEdge2Curve_node)

            cmds.setAttr(d3_polyEdge2Curve_node + '.degree', 1)

            # Rebuild the base-wire NURBS curve generated from the downstream wire node if exists.
            ds_crv_node = cmds.listConnections(d3_polyEdge2Curve_node + '.outputcurve', source=False, destination=True)[0]
            ds_crv_ds_node_list = cmds.listConnections(ds_crv_node + '.worldSpace[0]', source=False, destination=True)
            for ds_crv_ds_node in ds_crv_ds_node_list:
                if 'wire' == cmds.objectType(ds_crv_ds_node):
                    ds_crv_wirebase_node_list = cmds.listConnections(ds_crv_ds_node + '.baseWire[0]', source=True,
                                                                     destination=False)
                    if None != ds_crv_wirebase_node_list:
                        ds_crv_wirebase_node = ds_crv_wirebase_node_list[0]
                        wirebase_shape_node = ds_crv_wirebase_node
                        if 'transform' == cmds.objectType(wirebase_shape_node):
                            wirebase_shape_node_list = cmds.listRelatives(wirebase_shape_node, children=True,
                                                                          type='shape')
                            if None != wirebase_shape_node_list:
                                wirebase_shape_node = wirebase_shape_node_list[0]
                                assert 'nurbsCurve' == cmds.objectType(wirebase_shape_node)

                        if 'nurbsCurve' == cmds.objectType(wirebase_shape_node):
                            crv_rebuild_spans = cmds.getAttr(wirebase_shape_node + '.spans')
                            cmds.rebuildCurve(wirebase_shape_node,
                                              rebuildType=0,  # uniform
                                              degree=1,
                                              spans=crv_rebuild_spans)

        if len(invalid_node_list) > 0:
            step_info += u'\n=============== 置1阶数为3的polyEdgeToCurve节点 #自动修正 ===============\n'
            step_info += u'标注：Muggle框架3阶曲线的构建代码有bug，仅使用1阶曲线防止网格扭曲。\n\n'
            step_info += u'以下degree属性为3的polyEdgeToCurve节点会输出3阶曲线:\n'

            for d3_polyEdge2Curve_node in invalid_node_list:
                step_info += (u'【{}】\n'.format(d3_polyEdge2Curve_node))

        step_info += '\n'
        if console_print and ('\n' != step_info):
            cmds.warning(step_info)

        return True, step_info

    # Checking Steps ---------------------------------------------------------------------------------------------------
    def search_forbidden_nodes(self, existing_node_dict, console_print=True):
        ''' Search nodes of types that are not implemented in the Muggle framework.
        we cannot pass the nodes graph parsing stage if any of such node exists and are not filtered.
        :return: bool, string
                 1) False if any node of the forbidden types found, else True
                 2) the names of the forbidden nodes found, categorized by types
        '''
        step_info = ''
        warning_info = ''

        builtin_nodetype_list = [
            # General
            'expression',
            'mute',

            # Modeling & Texturing
            # 'rebuildSurface',
            'polyTweakUV'
            'polyTransfer',
            'deleteComponent',
            'deleteUVSet'

            # Rigging
            'deformTwist',
            'deltaMush',
            'cMuscleSurfAttach',

            # Misc
            'remapColor'
        ]
        builtin_nodes_dict = {}
        for builtin_nodetype in builtin_nodetype_list:
            if builtin_nodetype in existing_node_dict.keys():
                builtin_nodes_dict[builtin_nodetype] = existing_node_dict[builtin_nodetype]

        # The LCA in-house Maya custom nodes not implemented in the Muggle framework.
        # Most of those nodes are used in the old facial rigging system and do not have a chance to be implemented.
        custom_nodetype_list = [
            # Mapping
            'lcBlendReader',
            'lcControllerReader',
            'lcCurveUVRebase',
            'lcCurveUVRemap',
            'lcCurveUVspaceScale',
            'lcDistributeWeightFromSurface',
            'lcInbetweenMapping',

            # Transformation
            'lcConvertCurveSurfaceSpace',
            'lcConvertCurveToUvSpace',
            'lcConvertCurveToWorldSpace',

            # Geometry
            'lcCurveRebuild',
            'lcCurveResample',
            'lcInterceptCurve',

            # Constraint
            'lcBoneTwist',
            'lcControllerFollow',

            # Deformer
            'lcCalculateDeltaCurve',
            'lcCurveDeformer',
            'lcCurveZipper',
            'lcCvSliderDeformer',
            'stretchMesh',
            # 'underworldBlendShape',

            # Skinning
            'lcCurveCVWeight',
            'lcCurveOffset',

            # Unknown
            'lcDeformerAttrReader',
            'lcNormalAlign',
            'lcNurbsSpans',
            'lcRunCmdLocator',
            'lcUniformCurveRebuild',
            'lcVisLocator',
            'curveColliderLocator'
        ]
        custom_nodes_dict = {}
        for custom_nodetype in custom_nodetype_list:
            if custom_nodetype in existing_node_dict.keys():
                custom_nodes_dict[custom_nodetype] = existing_node_dict[custom_nodetype]

        if ((len(builtin_nodes_dict.keys()) > 0) or (len(custom_nodes_dict.keys()) > 0)):
            step_info += u'\n=============== Muggle框架未实现的节点 #手动/酌情修正 ===============\n'

            if (len(builtin_nodes_dict.keys()) > 0):
                step_info += u'下列Maya内置节点未在Muggle框架中实现，需要手动修正:\n'

                for builtin_nodetype in builtin_nodes_dict.keys():
                    step_info += '--- {} ---\n'.format(builtin_nodetype)
                    for builtin_node in builtin_nodes_dict[builtin_nodetype]:
                        step_info += u'【{}】\n'.format(builtin_node)
                    step_info += '\n'

            if (len(custom_nodes_dict.keys()) > 0):
                warning_info += u'下列Maya自定义节点未在Muggle框架中实现，需要酌情修正:\n'

                for custom_nodetype in custom_nodes_dict.keys():
                    warning_info += '--- {} ---\n'.format(custom_nodetype)
                    for custom_node in custom_nodes_dict[custom_nodetype]:
                        warning_info += u'【{}】\n'.format(custom_node)
                    warning_info += '\n'

        if console_print and ('' != step_info):
            cmds.warning(step_info + warning_info)

        step_info += '\n'
        # return ((0 == builtin_nodes_dict.keys()) and (0 == custom_nodes_dict.keys())), step_info
        return (0 == len(builtin_nodes_dict.keys())), step_info

    def search_unfrozen_meshtransforms(self, existing_node_dict, console_print=True):
        ''' Search mesh nodes whose corresponding transforms have non-zero translation vectors,
        non-zero rotation vectors or non-unit scale vectors.
        Note that we ignore such meshes that are hidden.
        :return: bool, string
                 1) False if any such mesh found, else True
                 2) the mesh node names whose transformations are not identity
                    i.e. translate is not (0, 0, 0)
                         rotate is not (0, 0, 0)
                         scale is not (1, 1, 1)
        '''
        if 'mesh' not in existing_node_dict:
            return True, ''

        step_info = ''
        invalid_node_list = []

        trans_compo_list = ['x', 'y', 'z']

        mesh_node_list = existing_node_dict['mesh']
        for mesh_node in mesh_node_list:
            # Skip the "Original" meshes.
            if True == cmds.getAttr(mesh_node + '.intermediateObject'):
                continue

            is_mesh_trans_unfrozen = False
            mesh_parent_node_list = cmds.listRelatives(mesh_node, parent=True, fullPath=True)
            if None != mesh_parent_node_list:
                mesh_trans_node = mesh_parent_node_list[0]
                assert 'transform' == cmds.objectType(mesh_trans_node)

                # # Skip the hidden meshes.
                # if not cmds.getAttr(mesh_trans_node+'.visibility'):
                #     continue

                for trans_compo in trans_compo_list:
                    if abs(cmds.getAttr(mesh_trans_node + '.t' + trans_compo)) > g_zero_threshold:
                        is_mesh_trans_unfrozen = True
                        break
                    if abs(cmds.getAttr(mesh_trans_node + '.r' + trans_compo)) > g_zero_threshold:
                        is_mesh_trans_unfrozen = True
                        break
                    if abs(1.0 - cmds.getAttr(mesh_trans_node + '.s' + trans_compo)) > g_zero_threshold:
                        is_mesh_trans_unfrozen = True
                        break

                if is_mesh_trans_unfrozen:
                    invalid_node_list.append(mesh_trans_node)

        if len(invalid_node_list) > 0:
            step_info += u'\n=============== 未被冻结变换(transform)的网格节点 #脚本修正# ===============\n'
            step_info += u'以下mesh节点对应的transform需要被冻结: \n'
            step_info += u'提示1.请点击Modify -> Freeze Transformations并修正由此产生的rig效果错误。\n'
            step_info += u'提示2.可使用脚本lcmuggle_rectify_skinned.py冻结已蒙皮的网格变换。\n'
            step_info += u'     脚本路径:Q:/Share/liaosheng/Rigging TD/Codes\n\n'

            for unfrozen_meshtrans in invalid_node_list:
                mesh_t = cmds.getAttr(unfrozen_meshtrans + '.translate')[0]
                mesh_r = cmds.getAttr(unfrozen_meshtrans + '.rotate')[0]
                mesh_s = cmds.getAttr(unfrozen_meshtrans + '.scale')[0]
                step_info += u'【{}】\n'.format(unfrozen_meshtrans.split('|')[-1])
                step_info += u'平移值（Translate）: ({:.3f}, {:.3f}, {:.3f})\n'.format(mesh_t[0], mesh_t[1], mesh_t[2])
                step_info += u'旋转值（Rotate): ({:.3f}, {:.3f}, {:.3f})\n'.format(mesh_r[0], mesh_r[1], mesh_r[2])
                step_info += u'缩放值（Scale）: ({:.3f}, {:.3f}, {:.3f})\n\n'.format(mesh_s[0], mesh_s[1], mesh_s[2])

        if console_print and ('' != step_info):
            cmds.warning(step_info)

        return (0 == len(invalid_node_list)), step_info

    def search_nonzero_rotaxes(self, existing_node_dict, console_print=True):
        ''' Search for transform and joint nodes whose "Rotate Axis" attributes are non-zero vectors.
        :return: bool, string
                 1) False if any such transform node found, else True
                 2) the names of the nodes that meet the conditions
        '''
        if ('transform' not in existing_node_dict) or ('joint' not in existing_node_dict):
            return True, ''

        step_info = ''
        invalid_trans_dict = {}
        invalid_jnt_dict = {}

        trans_node_list = existing_node_dict['transform']
        for trans_node in trans_node_list:
            trans_node_rotaxis = cmds.getAttr(trans_node + '.rotateAxis')[0]
            for compo in trans_node_rotaxis:
                if abs(compo) > g_zero_threshold:
                    info_str = u' 其"Rotate Axis"旋转轴向量为: ({:.3f}, {:.3f}, {:.3f})\n'.format(trans_node_rotaxis[0],
                                                                                               trans_node_rotaxis[1],
                                                                                               trans_node_rotaxis[2])
                    invalid_trans_dict[trans_node] = info_str
                    break

        if (len(invalid_trans_dict.keys()) > 0):
            step_info += '\n'

        jnt_node_list = existing_node_dict['joint']
        for jnt_node in jnt_node_list:
            jnt_node_rotaxis = cmds.getAttr(jnt_node + '.rotateAxis')[0]
            for compo in jnt_node_rotaxis:
                if abs(compo) > g_zero_threshold:
                    info_str = u' 其旋转轴向量为: ({:.3f}, {:.3f}, {:.3f})\n'.format(jnt_node_rotaxis[0],
                                                                                  jnt_node_rotaxis[1],
                                                                                  jnt_node_rotaxis[2])
                    invalid_trans_dict[jnt_node] = info_str
                    break

        if ((len(invalid_trans_dict.keys()) > 0) or (len(invalid_jnt_dict.keys())) > 0):
            step_info += u'\n=============== 旋转轴不为零向量的变换（transform）及骨骼(joint)节点 #手动修正# ===============\n'
            step_info += u'(请置零相应节点Attribute Editor -> Transform Attributes -> Rotate Axis属性的值，然后处理rig效果异常。)\n'
            step_info += u'Muggle框架transform节点包含rotateAxis参数的运算存在bug。\n'
            step_info += u'提示.可参考脚本lcmuggle_clear_constraint_joint_rotaxis.py脚本处理被约束的rotateAxis属性。\n'
            step_info += u'     脚本路径:Q:/Share/liaosheng/Rigging TD/Codes\n\n'

            if (len(invalid_trans_dict.keys()) > 0):
                step_info += u'以下transform节点的"Rotate Axis"属性不为(0, 0, 0):\n'

                for trans_node in invalid_trans_dict.keys():
                    step_info += u'【{}】'.format(trans_node) + invalid_trans_dict[trans_node]

                step_info += '\n'

            if (len(invalid_jnt_dict.keys()) > 0):
                step_info += u'以下joint节点的"Rotate Axis"属性不为(0, 0, 0):\n'

                for jnt_node in invalid_jnt_dict.keys():
                    step_info += u'【{}】'.format(jnt_node) + invalid_trans_dict[jnt_node]

                step_info += '\n'

        if console_print and ('' != step_info):
            cmds.warning(step_info)

        return ((0 == len(invalid_trans_dict.keys())) and (0 == len(invalid_jnt_dict.keys()))), step_info

    # DEPRECATED
    def search_rigpass_hiding_meshes(self, existing_node_dict, console_print=True):
        ''' Search for any controller's attribute that switches the visibility of meshes.
        :return: bool, string
                 1) False if any such attribute found, else True
                 2) the meshes or the groups they are under who are hidden
        '''
        if 'mesh' not in existing_node_dict:
            return True, ''

        step_info = ''
        found_rigpass = False

        # --------------------------------------------------------------------------------------------------------------
        # The attributes that don't count as Rig Passes
        rigpass_ignore_list = ['visibility_ctrl.highlight_box']
        # --------------------------------------------------------------------------------------------------------------
        rigpass_meshgrp_dict = {}

        mesh_node_list = existing_node_dict['mesh']
        hidden_mesh_trans_list = []
        for mesh_node in mesh_node_list:
            if not cmds.getAttr(mesh_node + '.intermediateObject'):
                mesh_trans_parent_list = cmds.listRelatives(mesh_node, parent=True)
                if None != mesh_trans_parent_list:
                    mesh_trans_parent = mesh_trans_parent_list[0]
                    if 'transform' == cmds.objectType(mesh_trans_parent):
                        mesh_node_path = cmds.listRelatives(mesh_trans_parent, fullPath=True)[0]
                        mesh_parent_node_list = mesh_node_path.split('|')[1:-1] or []
                        for mesh_parent_node in mesh_parent_node_list:
                            if 'transform' == cmds.objectType(mesh_parent_node) and \
                                    not cmds.getAttr(mesh_parent_node + '.visibility'):
                                hidden_mesh_trans_list.append(mesh_parent_node)

        for hidden_mesh_trans_node in hidden_mesh_trans_list:
            plug_in_path_list = self.traverse_plugs_in_DAG(hidden_mesh_trans_node + '.visibility')
            if len(plug_in_path_list) > 1:
                rigpass_ignored = False
                for rigpass_ignored_attr in rigpass_ignore_list:
                    if rigpass_ignored_attr in plug_in_path_list[-1]:
                        rigpass_ignored = True

                if rigpass_ignored:
                    continue

                found_rigpass = True
                rig_pass_ctrl_attr = plug_in_path_list[-1]

                if rig_pass_ctrl_attr not in rigpass_meshgrp_dict:
                    rigpass_meshgrp_dict[rig_pass_ctrl_attr] = set()

                rigpass_meshgrp_dict[rig_pass_ctrl_attr].add(hidden_mesh_trans_node)

        if found_rigpass:
            step_info = u'\n=============== 被Rig Pass隐藏的网格(mesh)节点 #自动修正# ===============\n' + \
                        u'标注: 此检查项已添加至Muggle编译预处理代码中，防止代码过滤掉这些被隐藏的网格。\n\n' + \
                        step_info

            for rigpass in rigpass_meshgrp_dict.keys():
                step_info += u'被Rig Pass "{}" 隐藏的网格（所在组）: \n'.format(rigpass)

                for meshgrp in rigpass_meshgrp_dict[rigpass]:
                    step_info += u'【{}】\n'.format(meshgrp)

                step_info += '\n'

        if console_print and ('' != step_info):
            cmds.warning(step_info)

        return (not found_rigpass), step_info

    def search_standalone_joints(self, existing_node_dict, console_print=True):
        ''' Search any joint within some node chain which does not start with an object post-fixed by "_ctrl" or "_ctrl__local"
        treating as a controller; or any joint where there is no such controller acting as its parent in the hierarchy.
        :return: bool, string
                 1) False if any such joint node found, else True
                 2) "standalone" joint node names
        '''
        if 'joint' not in existing_node_dict:
            return True, ''

        ignored_keyword_list = ['_data_jnt', '_guide', 'face_M_1_base_bind', 'face_root_bind']

        step_info = ''
        invalid_node_list = []

        jnt_node_list = existing_node_dict['joint']
        for jnt_node in jnt_node_list:
            is_jnt_standalone = True

            # Pass 0: Omit joints with specified keywords.
            for ignored_keyword in ignored_keyword_list:
                if ignored_keyword in jnt_node:
                    is_jnt_standalone = False
                    break

            # Pass 1: Omit the joints with a parent joint; or joints in an IK chain.
            if is_jnt_standalone:
                jnt_node_parent_list = cmds.listRelatives(jnt_node, parent=True)
                if None != jnt_node_parent_list:
                    if 'joint' == cmds.objectType(jnt_node_parent_list[0]):
                        is_jnt_standalone = False
                # TODO Detect joints controlled by some IK handle.

            # Pass 2: Omit the joints constrained by other transform or joint nodes.
            if is_jnt_standalone:
                transplug_connectedlist = list_connected_transplug_lambda(jnt_node)
                if len(transplug_connectedlist) > 0:
                    is_jnt_standalone = False

                if is_jnt_standalone:
                    jnt_node_child_list = cmds.listRelatives(jnt_node, children=True) or []
                    for jnt_node_child in jnt_node_child_list:
                        if cmds.objectType(jnt_node_child) in \
                                ['parentConstraint', 'pointConstraint', 'scaleConstraint',
                                 'aimConstraint', 'orientConstraint']:
                            is_jnt_standalone = False
                            break

                    if is_jnt_standalone:
                        jnt_node_parent_list = cmds.listRelatives(jnt_node, parent=True)
                        if None != jnt_node_parent_list:
                            if None != cmds.listRelatives(jnt_node_parent_list[0], type='follicle'):
                                is_jnt_standalone = False

                    if is_jnt_standalone:
                        jnt_node_upstream_list = cmds.listConnections(jnt_node + '.translateX', source=True, destination=False)
                        if None != jnt_node_upstream_list and \
                                'lcParentConstraint' == cmds.objectType(jnt_node_upstream_list[0]):
                            is_jnt_standalone = False

            # Pass 3: Omit the joints whose transform ancestors are constrained by other transform or joint nodes.
            if is_jnt_standalone:
                jnt_node_ancestor_path = cmds.listRelatives(jnt_node, parent=True, fullPath=True)
                if None != jnt_node_ancestor_path:
                    jnt_node_ancestor_list = jnt_node_ancestor_path[0].split('|')[1:]  # The path string starts with a bar character.
                    for jnt_node_ancestor in jnt_node_ancestor_list:
                        if is_jnt_standalone:
                            ancestor_node_type = cmds.objectType(jnt_node_ancestor)
                            if None != cmds.listRelatives(jnt_node_ancestor, type='follicle'):
                                is_jnt_standalone = False
                                break
                            elif (ancestor_node_type in ['transform', 'joint']):
                                transplug_connectedlist = list_connected_transplug_lambda(jnt_node_ancestor)
                                if len(transplug_connectedlist) > 0:
                                    is_jnt_standalone = False
                                    break

                                ancestor_node_child_list = cmds.listRelatives(jnt_node_ancestor, children=True) or []
                                for ancestor_node_child in ancestor_node_child_list:
                                    if cmds.objectType(ancestor_node_child) in \
                                            ['parentConstraint', 'pointConstraint', 'scaleConstraint',
                                             'aimConstraint', 'orientConstraint']:
                                        is_jnt_standalone = False
                                        break

            # Pass 4: Search transform or joint nodes as ancestors in the hierarchy post-fixed by the string "_ctrl" or "_ctrl__local".
            if is_jnt_standalone:
                jnt_node_ancestor_path = cmds.listRelatives(jnt_node, parent=True, fullPath=True)
                if None != jnt_node_ancestor_path:
                    jnt_node_ancestor_list = jnt_node_ancestor_path[0].split('|')[ 1:]  # The path string starts with a bar character.
                    for jnt_node_ancestor in jnt_node_ancestor_list:
                        ancestor_node_type = cmds.objectType(jnt_node_ancestor)
                        if (ancestor_node_type in ['transform', 'joint']) and \
                                (jnt_node_ancestor.endswith('_ctrl') or jnt_node_ancestor.endswith('_ctrl__local')):
                            is_jnt_standalone = False
                            break

            # Pass 5: Search such nodes post-fixed by "_ctrl" or "_ctrl__local" in the upstream of the node chain.
            if is_jnt_standalone:
                if not self.search_controller_in_upstream(jnt_node + '.translate'):
                    if not self.search_controller_in_upstream(jnt_node + '.rotate'):
                        if not self.search_controller_in_upstream(jnt_node + '.scale'):
                            if self.search_controller_in_upstream(jnt_node + '.inverseScale'):
                                is_jnt_standalone = False
                        else:
                            is_jnt_standalone = False
                    else:
                        is_jnt_standalone = False
                else:
                    is_jnt_standalone = False

            # Pass 6: Search such nodes post-fixed by "_ctrl" or "_ctrl__local" in the upstream of the node chain
            # where the parent transform of the joint post-fixed by "_pri", "_sec", "_dri", "_con", "_ofs" or "_grp" locates.
            if is_jnt_standalone:
                for postfix in ['_pri', '_sec', '_dri', '_con', '_ofs', '_grp']:
                    jnt_grp_node = jnt_node + postfix
                    if cmds.objExists(jnt_grp_node):
                        assert 'transform' == cmds.objectType(jnt_grp_node)
                        if not self.search_controller_in_upstream(jnt_grp_node + '.translate'):
                            if not self.search_controller_in_upstream(jnt_grp_node + '.rotate'):
                                if self.search_controller_in_upstream(jnt_grp_node + '.scale'):
                                    is_jnt_standalone = False
                                    break
                            else:
                                is_jnt_standalone = False
                                break
                        else:
                            is_jnt_standalone = False
                            break

            if is_jnt_standalone:
                invalid_node_list.append(jnt_node)

        if len(invalid_node_list) > 0:
            step_info += u'\n=============== 不与控制器直接或间接相连的骨骼(joint)节点 #酌情修正# ===============\n'
            step_info += u'Muggle框架的输入均为控制器，不受控制器影响的骨骼会被其过滤掉。'
            step_info += u'以下joint节点不受后缀带有_ctrl或者_ctrl__local的控制器功能节点影响: \n'
            step_info += u'提示.可参考脚本lcmuggle_spec_preprocessing.py的process_standalone_bones()函数。\n'
            step_info += u'     脚本路径:Q:/Share/liaosheng/Rigging TD/Codes\n\n'

            for standalone_jnt in invalid_node_list:
                step_info += u'【{}】\n'.format(standalone_jnt)

        step_info += '\n'
        if console_print and ('\n' != step_info):
            cmds.warning(step_info)

        return (0 == len(invalid_node_list)), step_info

    def search_invalid_iksolvers(self, existing_node_dict, console_print=True):
        ''' Search IK Solver nodes:
        1. of ikSCsolver type whose related ikHandle's "D World Up Matrix" plug has input some connection.
        :return: bool, string
                 1) False if any such IK Solver found, else True
                 2) the names of the invalid IK Solver nodes who meet the conditions
        '''
        if ('ikHandle' not in existing_node_dict) or ('ikSCsolver' not in existing_node_dict):
            return True, ''

        step_info = ''
        invalid_node_list = []

        ikhandle_node_list = existing_node_dict['ikHandle']
        for ikhandle_node in ikhandle_node_list:
            iksolver_node_list = cmds.listConnections(ikhandle_node + '.ikSolver',
                                                      source=True, destination=False) or []
            assert len(iksolver_node_list) > 0
            if not 'ikSCsolver' == cmds.objectType(iksolver_node_list[0]):
                continue

            dwumatrix_plug_connected_list = cmds.listConnections(ikhandle_node + '.dWorldUpMatrix',
                                                                 source=True, destination=False) or []
            if len(dwumatrix_plug_connected_list) > 0:
                invalid_node_list.append(ikhandle_node)

        if (len(invalid_node_list) > 0):
            step_info += u'\n=============== 不符合限制条件的ikHandle节点 #手动修正# ===============\n'
            step_info += u'以下关联ikSCsolver节点的ikHandle节点其"D World Up Matrix"属性plug有连接,' \
                         u'但Muggle框架IK节点没有包含dWorldUpMatrix参数的重载函数。\n' \
                         u'提示: 请直接断开该属性的连接。\n\n'

            for ikhandle_node in invalid_node_list:
                step_info += u'【{}】\n'.format(ikhandle_node)

        step_info += '\n'
        if console_print and ('\n' != step_info):
            cmds.warning(step_info)

        return (0 == len(invalid_node_list)), step_info

    def search_invalid_constraints(self, existing_node_dict, console_print=True):
        ''' Search any constraint nodes whose only weight attribute's value is zero and
        whose plug is not connected to any plug.
        This condition might cause crash during the Muggle rig compilation.
        :return: bool, string
                 1) False if any such constraint node found, else True
                 2) such constraint node names

        '''
        if ('parentConstraint' not in existing_node_dict) and \
           ('pointConstraint' not in existing_node_dict) and \
           ('scaleConstraint' not in existing_node_dict) and \
           ('aimConstraint' not in existing_node_dict) and \
           ('orientConstraint' not in existing_node_dict):
            return True, ''

        step_info = ''
        invalid_node_list = []

        constraint_type_list = ['parentConstraint', 'pointConstraint', 'scaleConstraint',
                                'aimConstraint', 'orientConstraint']
        for constraint_type in constraint_type_list:
            if constraint_type not in existing_node_dict:
                continue
            constraint_node_list = existing_node_dict[constraint_type]

            for constraint_node in constraint_node_list:
                attr_list = cmds.listAttr(constraint_node)
                weight_attr_list = [attr for attr in attr_list if None != re.search('W\d', attr)]

                if 1 == len(weight_attr_list):
                    weight_attr = constraint_node + '.' + weight_attr_list[0]
                    weight_val = cmds.getAttr(weight_attr)
                    if (0 == weight_val) and (None == cmds.listConnections(weight_attr, source=True, destination=False)):
                        invalid_node_list.append(constraint_node)

        if len(invalid_node_list) > 0:
            step_info += u'\n=============== 唯一的权重属性其值为0的约束(constraint)节点 #酌情修正# ===============\n'
            step_info += u'以下约束类节点的权重属性值为0且plug不与任何节点属性连接:\n'\
                         u'权重属性可能会在Muggle编译预处理时被判定为未初始化（uninitialized）而造成Python解释器崩溃。\n\n'

            for invalid_node in invalid_node_list:
                step_info += invalid_node + '\n'

        step_info += '\n'
        if console_print and ('\n' != step_info):
            cmds.warning(step_info)

        return (0 == len(invalid_node_list)), step_info

    def search_invalid_skinclusters(self, existing_node_dict, console_print=True):
        ''' Search skinCluster nodes:
        1. whose "Normalize Weights" attributes are not of the value "Interactive".
        2. whose "Bind Pre Matrix" list does not match their "Matrix" list.
        3. whose inputs（source) are not shape nodes.

        1 may cause mesh deformation inconsistency because Muggle only supports "Interactive" normalize weights type.
        2 and 3 may lead to crash during Muggle graph parsing.

        :return: bool, string
                 1) False if any such skinCluster found, else True
                 2) the names of the skinCluster nodes who meet the conditions
        '''
        if 'skinCluster' not in existing_node_dict:
            return True, ''

        step_info = ''
        found_invalid_skincluster = False

        # --------------------------------------------------------------------------------------------------------------
        check_dict = {1:True, 2:False, 3:False}
        # --------------------------------------------------------------------------------------------------------------
        weighttype_failed_dict = {}
        matrixmatch_failed_dict = {}
        inputstype_failed_dict = {}

        skincluster_nmweights_dict = {0: 'None', 1: 'Interactive', 2: 'Post'}

        skincluster_node_list = existing_node_dict['skinCluster']
        for skincluster_node in skincluster_node_list:
            # Check 1: Search skinClusters with normalizeWeights attribute values other than "Interactive".
            if check_dict[1]:
                if 1 != cmds.getAttr(skincluster_node + '.normalizeWeights'):
                    info_str = u' 其"Normalize Weights"属性值为: {}\n'.format(
                        skincluster_nmweights_dict[cmds.getAttr(skincluster_node + '.normalizeWeights')])

                    weighttype_failed_dict[skincluster_node] = info_str

            # Check 2: Search skinClusters whose "Matrix" and "Bind Pre Matrix" list do not match.
            if check_dict[2]:
                matrixattr_idx_list = []
                matrixattr_vacidx_list = []
                bpmatrixattr_idx_list = []
                bpmatrixattr_vacidx_list = []

                self.search_vacant_attrlist_elem(skincluster_node, 'matrix', None, plugTypeEnum.input,
                                                 matrixattr_idx_list, matrixattr_vacidx_list)
                self.search_vacant_attrlist_elem(skincluster_node, 'bindPreMatrix', None, plugTypeEnum.input,
                                                 bpmatrixattr_idx_list, bpmatrixattr_vacidx_list)

                matrixattr_valididx_list = [idx for idx in matrixattr_idx_list if idx not in matrixattr_vacidx_list]
                bpmatrixattr_valididx_list = [idx for idx in bpmatrixattr_idx_list if idx not in bpmatrixattr_vacidx_list]
                if ((len(bpmatrixattr_valididx_list) > 0) and (matrixattr_valididx_list != bpmatrixattr_valididx_list)):
                    info_str = u'其"Bind Pre Matrix"输入数组有连接的plugs索引: {}\n'.format(bpmatrixattr_valididx_list)
                    info_str += u'其"Matrix"输入数组有连接的plugs索引: {}\n\n'.format(matrixattr_valididx_list)

                    matrixmatch_failed_dict[skincluster_node] = info_str

            # Check 3: Search skinClusters whose input (source) is not shape nodes;
            # skinClusters with non-shape sources are not initialized and will cause the compiler crash.
            if check_dict[3]:
                shape_node_type_list = ['mesh', 'nurbsCurve', 'nurbsSurface', 'lattice']

                source_is_shape = False
                plug_in_path_list = []

                attr_list = cmds.listAttr(skincluster_node, multi=True)
                for attr in attr_list:
                    if 'input[' in attr and 'inputGeometry' in attr:
                        plug_in_path_list = self.traverse_plugs_in_DAG(skincluster_node + '.' + attr,
                                                                       dir=traversalDirEnum.eUpStream)

                        for plug in plug_in_path_list:
                            node_name = plug.split('.')[0]
                            node_type = cmds.objectType(node_name)
                            if node_type in shape_node_type_list:
                                source_is_shape = True

                if not source_is_shape:
                    info_str = ' 其上游节点链没有shape型节点: {}\n\n'.format(plug_in_path_list)

                    inputstype_failed_dict[skincluster_node] = info_str


        if len(weighttype_failed_dict.keys()) > 0:
            found_invalid_skincluster = True

            step_info += u'以下skinCluster节点的"Normalize Weights"属性值不为"Interactive":\n'
            step_info += u'(Muggle框架只支持该属性值，否则会造成编译后蒙皮变形效果的不一致)\n\n'

            for key in weighttype_failed_dict.keys():
                step_info += (u'【{}】'.format(key) + weighttype_failed_dict[key])

            step_info += '\n'

        if len(matrixmatch_failed_dict.keys()) > 0:
            found_invalid_skincluster = True

            step_info += u'以下skinCluster节点的"Bind Pre Matrix"和"Matrix"输入数组有连接的plug索引不对应:\n'
            step_info += u'缺失连接的plug可能会在Muggle编译预处理时'\
                         u'被判定为未初始化（uninitialized）而造成Python解释器崩溃。\n\n'

            for key in matrixmatch_failed_dict.keys():
                step_info += (u'【{}】'.format(key) + '\n' + matrixmatch_failed_dict[key])

            step_info += '\n'

        if len(inputstype_failed_dict.keys()) > 0:
            found_invalid_skincluster = True

            step_info += u'以下skinCluster节点所在节点链的源头不是shape类型节点:\n'
            step_info += u'节点input plug可能会在Muggle编译预处理时'\
                         u'被判定为未初始化（uninitialized）而造成Python解释器崩溃。\n\n'

            for key in inputstype_failed_dict.keys():
                step_info += (u'【{}】'.format(key) + inputstype_failed_dict[key])

            step_info += '\n'

        if (found_invalid_skincluster):
            step_info = u'\n=============== 不符合限制条件的蒙皮(skinCluster)节点 #手动/酌情修正# ===============\n' + step_info
        else:
            step_info += '\n'

        if console_print and ('\n' != step_info):
            cmds.warning(step_info)

        return (not found_invalid_skincluster), step_info

    def search_invalid_curveinfos(self, existing_node_dict, console_print=True):
        ''' Search curveInfo nodes with vacant output list elements.
        :return: bool, string
                 1) False if any such curveInfo found, else True
                 2) the names of the curveinfo nodes
                    whose "Control Points" output list contains plugs without connections
        '''
        if 'curveInfo' not in existing_node_dict:
            return True, ''

        step_info = ''
        invalid_node_dict = {}

        curveinfo_node_list = existing_node_dict['curveInfo']
        for curveinfo_node in curveinfo_node_list:
            cpattr_idx_list = []
            cpattr_vacidx_list = []
            b_any_cpattr_vacant = self.search_vacant_attrlist_elem(curveinfo_node, 'controlPoints', 'Value',
                                                                   plugTypeEnum.output,
                                                                   cpattr_idx_list, cpattr_vacidx_list)

            if b_any_cpattr_vacant:
                info_str = u' 其输出数组没有连接的plugs索引: {}\n'.format(cpattr_vacidx_list)

                invalid_node_dict[curveinfo_node] = info_str

        if (len(invalid_node_dict.keys()) > 0):
            step_info += u'\n=============== 输出数组有空元素的curveInfo节点 #酌情修正# ===============\n'
            step_info += u'curveInfo节点输出数组plugs没有连接会导致Muggle编译预处理崩溃。'
            step_info += u'提示.可参考脚本lcmuggle_spec_preprocessing.py的pad_curveinfo_vacant_outputs()函数。\n'
            step_info += u'     脚本路径:Q:/Share/liaosheng/Rigging TD/Codes\n\n'
            step_info += u'以下curveInfo节点的"Control Points"输出数组存在无连接的plugs:\n'

            for curveinfo_node in invalid_node_dict.keys():
                step_info += u'【{}】'.format(curveinfo_node) + invalid_node_dict[curveinfo_node]

        step_info += '\n'
        if console_print and ('\n' != step_info):
            cmds.warning(step_info)

        return (0 == len(invalid_node_dict.keys())), step_info

    def search_invalid_lcchainvolumes(self, existing_node_dict, console_print=True):
        ''' Search lcChainVolume nodes with no stretchVolumeCurve and squashVolumeCurve input connections.
        :return: bool, string
                 1) False if any such lcChainVolume found, else True\
                 2) the lcChainVolume nodes that do not the demands
        '''
        if 'lcChainVolume' not in existing_node_dict:
            return True, ''

        step_info = ''
        invalid_node_dict = {}

        lcchainvolume_node_list = existing_node_dict['lcChainVolume']
        for lcchainvolume_node in lcchainvolume_node_list:
            stretch_crv_input_list = cmds.listConnections(lcchainvolume_node + '.stretchVolumeCurve',
                                                          source=True, destination=False) or []
            squash_crv_input_list = cmds.listConnections(lcchainvolume_node + '.squashVolumeCurve',
                                                         source=True, destination=False) or []
            if 0 == len(stretch_crv_input_list) or 0 == len(squash_crv_input_list):
                info_str = ''
                if 0 == len(stretch_crv_input_list):
                    info_str += u' 其"Stretch Volume Curve"输入plug没有连接。\n'
                if 0 == len(squash_crv_input_list):
                    info_str += u' 其"Squash Volume Curve"输入plug没有连接。\n'

                info_str += '\n'
                invalid_node_dict[lcchainvolume_node] = info_str

        if (len(invalid_node_dict.keys()) > 0):
            step_info += u'\n=============== 输入plugs没有连接的lcChainVolume节点 #手动修正# ===============\n'
            step_info += u'"Stretch/Squash Volume Curve"属性没有连接可能会在Muggle编译预处理时'\
                         u'被判定为未初始化（uninitialized）而造成Python解释器崩溃。\n'
            step_info += u'提示.可参考脚本lcmuggle_spec_preprocessing.py的repair_lcchainvolume_curves()函数。\n'
            step_info += u'     脚本路径:Q:/Share/liaosheng/Rigging TD/Codes\n\n'

            for lcchainvolume_node in invalid_node_dict.keys():
                step_info += u'【{}】'.format(lcchainvolume_node) + '\n' + invalid_node_dict[lcchainvolume_node]

        if console_print and ('' != step_info):
            cmds.warning(step_info)

        return (0 == len(invalid_node_dict.keys())), step_info

    # Utility Functions ------------------------------------------------------------------------------------------------
    def create_existing_nodes_dictionary(self):
        ''' Store all nodes in this rig asset into a dictionary using their types as the keys.
        :return: dictionary of the format: {node_type:node_names_list}
        '''
        existing_node_list = cmds.ls()
        existing_node_type_set = set()
        existing_node_dict = {}
        for maya_node in existing_node_list:
            node_type = cmds.objectType(maya_node)
            existing_node_type_set.add(node_type)

        for maya_node_type in existing_node_type_set:
            existing_node_dict[maya_node_type] = []

        for maya_node in existing_node_list:
            node_type = cmds.objectType(maya_node)
            existing_node_dict[node_type].append(maya_node)

        return existing_node_dict

    def traverse_plugs_in_DAG(self,
                              root_plug_name, dir=traversalDirEnum.eDownStream):
        '''
        :param root_plug_name: string
                               the attribute to begin with
        :param dir:traversalDirEnum
                   the traversal direction; any value not being 'downstream' will be treated as 'upstream'
        :return: list
                 contains the names of node plugs connected in the node chain where the root plug locates in
        '''

        import maya.OpenMaya as OpenMaya  # using Maya Python API 1.0

        assert cmds.objExists(root_plug_name)

        # Translate the parameters from string to OpenMaya's data-structures
        root_node_name = root_plug_name.split('.')[0]
        root_node_attr = root_plug_name.split('.')[-1]  # can be something like input[0].inputGeometry

        root_node = OpenMaya.MObject()
        sel_list = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getSelectionListByName(root_node_name, sel_list)
        sel_list.getDependNode(0, root_node)
        root_node_fn = OpenMaya.MFnDependencyNode(root_node)
        root_plug = root_node_fn.findPlug(root_node_attr)

        if traversalDirEnum.eDownStream == dir:
            dir = OpenMaya.MItDependencyGraph.kDownstream
        else:
            dir = OpenMaya.MItDependencyGraph.kUpstream

        dag_it = OpenMaya.MItDependencyGraph(root_plug,
                                             dir,
                                             OpenMaya.MItDependencyGraph.kPlugLevel,
                                             OpenMaya.MItDependencyGraph.kDepthFirst)

        # Do the traversal process.
        dag_it.reset()
        plug_path = OpenMaya.MPlugArray()
        plug_in_path_list = []

        while not dag_it.isDone():
            dag_it.getPlugPath(plug_path)
            assert None != plug_path
            current_plug = plug_path[0].name()

            plug_in_path_list.append(current_plug)

            dag_it.next()

        return plug_in_path_list

    # TODO: Check if the attribute exists for the given node type in this function.
    def search_vacant_attrlist_elem(self,
                                    node_name, listattr_name, listsubattr_name=None,
                                    attr_type=plugTypeEnum.input, attr_idx_reflist=[], attr_vacidx_reflist=[]):
        '''
        :param node_name: string
                          the name of the node
        :param listattr_name: string
                              the name of the node's list attribute
        :param attr_type: plugTypeEnum
                          indicates if the attribute plug is input or output
        :param attr_idx_reflist: list
                                 contains the indices of the attribute list non-empty elements
        :param attr_vacidx_reflist: list
                                    contains the indices of the attribute list empty elements
        :return: boolean
                 if the attribute list contains any empty element
        '''
        assert None != node_name
        assert None != listattr_name
        assert cmds.objExists(node_name)
        assert isinstance(attr_idx_reflist, list)
        assert isinstance(attr_vacidx_reflist, list)
        del attr_idx_reflist[:]
        del attr_vacidx_reflist[:]

        node_type = cmds.objectType(node_name)

        attr_list = cmds.listAttr(node_name, multi=True)
        for attr in attr_list:
            if None == listsubattr_name:
                if listattr_name + '[' in attr:
                    attr_idx_reflist.append(int(attr[-2]))
            else:
                if ((listattr_name + '[') in attr) and (listsubattr_name not in attr):
                    attr_idx_reflist.append(int(attr[-2]))

        attr_idx_reflist = list(set(attr_idx_reflist))
        attr_idx_reflist.sort()  # ascending order

        if len(attr_idx_reflist) > 0:  # Empty list does not have any sub-attribute with the indexing operator "[]".
            attr_idx_max = attr_idx_reflist[-1]
            for idx in range(0, attr_idx_max + 1):
                b_vacant_elem = False
                if idx not in attr_idx_reflist:
                    b_vacant_elem = True
                else:
                    b_input_attr = (plugTypeEnum.input == attr_type)
                    connected_node_list = cmds.listConnections(node_name + '.' + listattr_name + '[{}]'.format(idx),
                                                               source=b_input_attr,
                                                               destination=(not b_input_attr)) or []
                    if 0 == len(connected_node_list):
                        b_vacant_elem = True

                if b_vacant_elem:
                    attr_vacidx_reflist.append(idx)

        attr_vacidx_reflist = list(set(attr_vacidx_reflist))
        attr_vacidx_reflist.sort()

        # if (0 == len(attr_idx_reflist)) and (0 == len(attr_vacidx_reflist)):
        #     cmds.warning('Node type {0} does not have the attribute {1}.'.format(node_type, listattr_name))

        return len(attr_vacidx_reflist) > 0

    def search_controller_in_upstream(self,
                                      jnt_plug):
        assert '.translate' in jnt_plug or \
               '.rotate' in jnt_plug or \
               '.scale' in jnt_plug or \
               '.inverseScale' in jnt_plug

        does_controller_exist = False

        plug_in_path_list = self.traverse_plugs_in_DAG(jnt_plug, dir=traversalDirEnum.eUpStream)
        for plug in plug_in_path_list:
            node_name = plug.split('.')[0]
            node_type = cmds.objectType(node_name)
            if (node_type in ['transform', 'joint']) and \
                    (node_name.endswith('_ctrl') or node_name.endswith('_ctrl__local')):
                does_controller_exist = True
                break

        return does_controller_exist

    # Other functions --------------------------------------------------------------------------------------------------
    def run_fix(self):
        '''Auto Fix'''
        pass

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty