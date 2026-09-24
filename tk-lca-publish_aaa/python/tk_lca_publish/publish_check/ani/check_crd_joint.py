# -*- coding:utf-8 -*-
# @Time:2024/5/15 下午4:45
import traceback
import maya.cmds as cmds
import pymel.core as pm


def find_polymesh_under_group(group_name):
    all_meshes = pm.listRelatives(group_name, children=True, allDescendents=True, type="mesh")
    return all_meshes


def find_skin_clusters(mesh):
    skin_clusters = []
    history_nodes = pm.listHistory(mesh, ha=1)
    for node in history_nodes:
        if pm.nodeType(node) == 'skinCluster':
            if node not in skin_clusters:
                skin_clusters.append(node)
    return skin_clusters


def find_joints_linked_to_skin_clusters(skin):
    infList = []
    infList = pm.skinCluster(skin, query=True, inf=True)
    return infList
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查crd镜头prp是否是骨骼单链"
        self.description = u"crd镜头不允许使用非骨骼单链的prp"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return
    def run_check(self):
        try:
            if not self.dialog.entity['name'].startswith('z1'):
                return ''
            if self.dialog.project['name'].lower() == 'xun':
                if int(self.dialog.entity['name'][-3:])<31 or 49<int(self.dialog.entity['name'][-3:])<321 or 321<int(self.dialog.entity['name'][-3:])<323 or int(self.dialog.entity['name'][-3:])>339:
                    if not cmds.ls('assets|prp'): return ''
                    prpgroup = cmds.listRelatives('assets|prp',c=1)
                    if not prpgroup: return ''
                    allList = []
                    for i in prpgroup:
                        chrname = i.split(':')[0]
                        if pm.objExists(chrname+':mesh_grp'):
                            mesh_group = chrname+':mesh_grp'
                        elif pm.objExists(chrname+':shape'):
                            mesh_group = chrname+':shape'
                        else:
                            print "cannot find mesh group"
                            continue
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
                        #jointList = pm.listRelatives(coreRigGrp, children=True, allDescendents=True, type="joint")
                        topJointList = []
                        for each in jointList:
                            if each.getParent() == []:
                                topJointList.append(each)
                            else:
                                if (each.getParent()).nodeType() != "joint":
                                    topJointList.append(each)
                        if len(topJointList) == 1:
                            topJointList = []
                        if topJointList:
                            allList.append(i)
                    if allList:
                        return u'以下prp资产超过一个骨骼链,不可以在crd镜头里使用：'+'\n'.join(allList)
                    else:
                        return ''
                else:
                    return ''
                    print 'Skip z1* seq z11031 to z11049,z11323 to z11339 !'
            else:
                if not cmds.ls('assets|prp'): return ''
                prpgroup = cmds.listRelatives('assets|prp',c=1)
                if not prpgroup: return ''
                allList = []
                for i in prpgroup:
                    chrname = i.split(':')[0]
                    if pm.objExists(chrname+':mesh_grp'):
                        mesh_group = chrname+':mesh_grp'
                    elif pm.objExists(chrname+':shape'):
                        mesh_group = chrname+':shape'
                    else:
                        print "cannot find mesh group"
                        continue
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
                    #jointList = pm.listRelatives(coreRigGrp, children=True, allDescendents=True, type="joint")
                    topJointList = []
                    for each in jointList:
                        if each.getParent() == []:
                            topJointList.append(each)
                        else:
                            if (each.getParent()).nodeType() != "joint":
                                topJointList.append(each)
                    if len(topJointList) == 1:
                        topJointList = []
                    if topJointList:
                        allList.append(i)
                if allList:
                    return u'以下prp资产超过一个骨骼链,不可以在crd镜头里使用：'+'\n'.join(allList)
                else:
                    return ''
        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        try:
            return ''
        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty