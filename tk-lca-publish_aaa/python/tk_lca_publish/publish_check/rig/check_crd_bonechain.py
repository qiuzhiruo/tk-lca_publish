# -*- coding:utf-8 -*-

#
# Copyright (c) 2022 Light Chaser Animation Studios. All Rights Reserved.
#
## File Name: check_crd_bonechain.py
# Author: Sheng (Raymond) Liao
# Date: June 2022
#

import os
import traceback

import maya.cmds as cmds

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查绑定CRD群集资产的主骨骼链是否为单链、是否存在断链'
        self.description = u'检查绑定CRD群集资产的主骨骼链是否为单链、是否存在断链'
        self.auto_fix = False
        self.duty = u'艺术家本人'
        return

    def run_check(self):

        bone_chain_root = '|master|rig|anim_rig|anim_skeletons_grp|root_bind'
        bone_grp_filter_list = ['anim_skeletons_grp']

        try:
            # muggle_forbidden_data_path = 'D:/liaosheng/Light Chaser Animation Studios/Rigging TD/Codes/LCA_RIG'
            check_passed, feedback_info = rig_crd_bonechain_check(bone_chain_root, bone_grp_filter_list)
            cmds.warning(feedback_info)
            if not check_passed:
                return feedback_info
            else:
                return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        pass

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

# Checking Functions ---------------------------------------------------------------------------------------------------
def rig_crd_bonechain_check(bone_chain_root, grp_filter_list=None):
    '''
    @param bone_chain_root: The root joint of the bone chain that all the joints to check need to be its descendants.
    @param grp_filter_list: The joints other than being parented under the groups in the list won't be checked.
    @return:
    '''
    feedback_info = '\n============================== RIG CRD Asset Bone-Chain Check ==============================\n'
    res = True
    bone_chain_root_name = bone_chain_root.split('|')[-1]

    mesh_list = cmds.ls(exactType='mesh')
    for mesh_node in mesh_list:
        if True == cmds.getAttr(mesh_node+'.intermediateObject'):
            continue

        # Note that the skinCluster node was placed exactly at the front of the skinned mesh shape node,
        # so we can use the "cmds.listConnections" command to find it.
        skincluster_node = cmds.listConnections(mesh_node+'.inMesh', source=True, destination=False)
        if None != skincluster_node and 'skinCluster' == cmds.objectType(skincluster_node[0]):
            skincluster_node = skincluster_node[0]
            # print('Mesh "{}" has the skinCluster "{}" node connected.'.format(mesh_node, skincluster_node))
            skincluster_influencer_list = cmds.skinCluster(skincluster_node, query=True, influence=True)
            if None == skincluster_influencer_list:
                # cmds.warning('[Crd Rig Check Bone-chain] The skinned mesh "{}" ' \
                #              'does not have any influence object.'.format(mesh_node))
                feedback_info += '[Crd Rig Check Bone-chain] The skinned mesh "{}" ' \
                                 'does not have any influence object.\n'.format(mesh_node)
                continue

            for influencer in skincluster_influencer_list:
                if 'joint' != cmds.objectType(influencer):
                    # cmds.warning('[Crd Rig Check Bone-chain] The skinned mesh "{}" has a ' \
                    #              'non-joint influence object "{}".'.format(mesh_node, influencer))
                    feedback_info += '[Crd Rig Check Bone-chain] The skinned mesh "{}" has a ' \
                                     'non-joint influence object "{}".\n'.format(mesh_node, influencer)
                    continue

                # cmds.select(influencer, replace=True)
                influence_dagpath_list = cmds.listRelatives(influencer, parent=True, fullPath=True)

                # if None == influence_dagpath_list:
                #     cmds.warning('skincluster_influencer_list: {}'.format(skincluster_influencer_list))
                #     cmds.warning('The influencer "{}" does not have a DAG path.'.format(influencer))

                assert None != influence_dagpath_list

                joint_needs_checking = True if (None == grp_filter_list) else False

                for influence_dagpath in influence_dagpath_list:
                    # Check 1. If the joint is not under the group filtered in, ignore it.
                    if None != grp_filter_list:
                        for grp_filtered_in in grp_filter_list:
                            if grp_filtered_in in influence_dagpath:
                                joint_needs_checking = True

                    if not joint_needs_checking:
                        # cmds.warning('[Crd Rig Check Bone-chain] Skip the joint "{}" ' \
                        #              'because it is not placed under group in the list: ' \
                        #              '{}.'.format(influencer, grp_filter_list))
                        feedback_info += '[Crd Rig Check Bone-chain] Skip the joint "{}" ' \
                                         'because it is not placed under group in the list: ' \
                                         '{}.\n'.format(influencer, grp_filter_list)
                        continue

                    # Check 2. If the joint is not a root joint's descendant, the check failed.
                    influence_parent_list = influence_dagpath.split('|')
                    if bone_chain_root not in influence_dagpath:
                        # cmds.warning('[Crd Rig Check Bone-chain] The joint "{}" binding mesh "{}" was not placed ' \
                        #              'in the single bone chain ' \
                        #              'taking "root_bind" as the root.'.format(influencer, mesh_node))
                        feedback_info += '[Crd Rig Check Bone-chain] The joint "{}" binding mesh "{}" was not placed ' \
                                         'in the single bone chain ' \
                                         'taking "{}" as the root.\n'.format(influencer, mesh_node, bone_chain_root_name)
                        res = False

                    # Check 3. If the joint's direct parent or children are not joints, neither do the check pass.
                    influence_parent = influence_parent_list[-1]
                    if 'joint' != cmds.objectType(influence_parent):
                        # cmds.warning('[Crd Rig Check Bone-chain] The joint "{}" parent "{}" binding mesh "{}" ' \
                        #              'is not a joint.'.format(influencer, influence_parent, mesh_node))
                        feedback_info += '[Crd Rig Check Bone-chain] The joint "{}" parent "{}" binding mesh "{}" ' \
                                         'is not a joint.\n'.format(influencer, influence_parent, mesh_node)
                        res = False

                    influence_child_list = cmds.listRelatives(influencer, children=True)
                    if None != influence_child_list:
                        for influence_child in influence_child_list:
                            if 'joint' != cmds.objectType(influence_child):
                                # cmds.warning('[Crd Rig Check Bone-chain] The joint "{}" child "{}" binding mesh "{}" ' \
                                #              'is not a joint.'.format(influencer, influence_parent, mesh_node))
                                feedback_info += '[Crd Rig Check Bone-chain] The joint "{}" child "{}" binding mesh "{}" ' \
                                                 'is not a joint.\n'.format(influencer, influence_parent, mesh_node)
                                res = False

    feedback_info += '============================== RIG CRD Asset Bone-Chain Check ==============================\n\n'
    return res, feedback_info