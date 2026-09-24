# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check asset geometry hierarchy
#
############################################

import traceback
import os
import re
import maya.cmds as mc
def find_polymesh_under_group(group_name):
    all_meshes = mc.listRelatives(group_name, children=True, allDescendents=True, type="mesh")
    return all_meshes

def find_skin_clusters(mesh):
    skin_clusters = []
    history_nodes = mc.listHistory(mesh,ha=1)
    for node in history_nodes:
        if mc.nodeType(node) == 'skinCluster':
            if node not in skin_clusters:
                skin_clusters.append(node)
    return skin_clusters

def find_joints_linked_to_skin_clusters(skin):
    infList = []
    infList = mc.skinCluster(skin, query=True, inf=True)
    return infList

def check_unreal_support():
    """
    check master move

    @param master: master
    @type master : str

    @param poly : poly
    @type poly : str

    @return  [double_moved_objs, none_moved_objs]
    @retval list
    """

    current_file_path = mc.file(query=True, sceneName=True)

    if not r'/crd/' in current_file_path:
        return

    coreRigGrp = 'anim_skeletons_grp'
    # Get all joints in the scene
    #jointList = mc.ls(type='joint')
    mesh_group = ""
    if mc.objExists('mesh_grp'):
        mesh_group = 'mesh_grp'
    elif mc.objExists('shape'):
        mesh_group = 'shape'
    else:
        mc.error("cannot find mesh group")

    found_meshes = find_polymesh_under_group(mesh_group)
    skinClusterLists = []
    for eachMesh in found_meshes:
        skin_clusters = find_skin_clusters(eachMesh)
        for skin in skin_clusters:
            if skin not in skinClusterLists:
                skinClusterLists.append(skin)

    jointLists = []
    for eachSkin in skinClusterLists:
        linked_joints = find_joints_linked_to_skin_clusters(eachSkin)
        for eachJoint in linked_joints:
            if eachJoint not in jointLists:
                jointLists.append(eachJoint)

    jointList = jointLists
    #jointList = mc.listRelatives(coreRigGrp, children=True, allDescendents=True, type="joint")

    topJointList = []
    for each in jointList:
        if mc.listRelatives(each, parent=True) == []:
            topJointList.append(each)
        else:
            if mc.listRelatives(each, parent=True):
                if mc.nodeType(mc.listRelatives(each, parent=True)[0]) != "joint":
                    topJointList.append(each)

    if len(topJointList) != 1:
        #mc.warning("Following joints has no parent:" + str(topJointList))
        pass
    else:
        topJointList = []

    # mc.select(topJointList)

    # get all the deformer nodes
    unSupportedDeformerList = []
    deformers = mc.ls(type="geometryFilter")
    for each in deformers:
        if mc.nodeType(each) != "tweak":
            if mc.nodeType(each) != "skinCluster":
                if mc.nodeType(each) != "blendShape":
                    if mc.nodeType(each) != "lcPoseDeformer":
                        unSupportedDeformerList.append(each)

    if len(unSupportedDeformerList) != 0:
        #mc.warning("List of un-supported deformers: " + str(unSupportedDeformerList))
        pass
    else:
        unSupportedDeformerList = []

    # get all the deformer nodes
    unSupportedSkinCluster = []
    skinCount = []
    unSupportedBlendShape = []
    BsCount = []
    geoList = mc.ls(type='mesh')
    for eachGeoMesh in geoList:
        if mc.listRelatives(str(eachGeoMesh), parent=True):
            eachGeo = mc.listRelatives(str(eachGeoMesh), parent=True)[0]
            BsCount = []
            skinCount = []
            listHis = []
            listHis = mc.listHistory(eachGeo)
            for eachHis in listHis:
                if mc.nodeType(eachHis) == "skinCluster":
                    if skinCount.count(eachHis) == 0:
                        skinCount.append(eachHis)
                if mc.nodeType(eachHis) == "blendShape":
                    if BsCount.count(eachHis) == 0:
                        BsCount.append(eachHis)

            if skinCount:
                if len(skinCount) > 1:
                    #mc.warning(str(eachGeo) + " has more than one skinCluster")
                    if unSupportedSkinCluster.count(eachGeo) == 0:
                        unSupportedSkinCluster.append(eachGeo)
                        print(eachGeo, skinCount)
                else:
                    pass

            if BsCount:
                if len(BsCount) > 1:
                    #mc.warning(str(eachGeo) + " has more than one blendShape")
                    if unSupportedBlendShape.count(eachGeo) == 0:
                        unSupportedBlendShape.append(eachGeo)
                else:
                    pass
    print 'index115'
    #allList = u'超过一个骨骼链: {},\n 不支持的变形器: {},\n 超过一个BS: {},\n 超过一个Skin: {}'.format(str(topJointList),str(unSupportedDeformerList),str(unSupportedBlendShape),str(unSupportedSkinCluster))
    allList = []
    #emptyList = []
    #return topJointList, unSupportedDeformerList, unSupportedBlendShape, unSupportedSkinCluster
    if topJointList:
        allList.extend(topJointList)
    if unSupportedDeformerList:
        allList.extend(unSupportedDeformerList)
    if unSupportedBlendShape:
        allList.extend(unSupportedBlendShape)
    if unSupportedSkinCluster:
        allList.extend(unSupportedSkinCluster)
    print 'index116'
    if not allList:
        print('single chain check pass')
        return
    return str(allList)


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查群集绑定是否满足进引擎的条件（非crd资产会自动跳过）'
        self.description = u'检查绑定是否符合进引擎的条件'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        allList = check_unreal_support()
        print 'index188'
        print allList
        if allList:
            message = str(allList)
            #message  = u'超过一个骨骼链: {},\n 不支持的变形器: {},\n 超过一个BS: {},\n 超过一个Skin: {}'.format(str(JointList),str(DeformerList),str(BSList),str(SkinList))
            #print message
            print 'index192'
            return message
        else:
            return

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
