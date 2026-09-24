# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Edward Sun
#
# Date: 2013.07
#
# Description: Check asset geometry hierarchy
#
############################################

import traceback
import maya.cmds as cmds
import os
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查anim_skeletons_grp下骨骼链是否为连续的树状结构。"
        self.description = u"anim_skeletons_grp所放的骨骼必须有个root，并且骨骼层级间不能被group打断。"
        self.auto_fix = False
        self.duty = u"艺术家本人 或 TD。"
        return

    def check_skeleton_chain(self):
        asset_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])
        if asset_info['sg_asset_type'] != 'crd':
            return u""
        cs=cmds.listRelatives('master|rig|anim_rig|anim_skeletons_grp')
        if not cs:
            print 'there is no children below the anim_skeletons_grp'
            return u""
        rootjnts=[]
        for c in cs:
            if cmds.nodeType(c)=='joint':
                rootjnts.append(c)
        if not len(rootjnts)==len(cs):
            print u"anim_skeletons_grp  only can include joint"
            return u"anim_skeletons_grp 下只能放骨骼"
        if len(rootjnts)>1:
            print u"anim_skeletons_grp  only can include only one root joint"
            return u"anim_skeleton_grp 下只能放一个root骨骼"
        rootjnt = rootjnts[0]
        cmds.select(rootjnt,hi=1)
        cmds.select(rootjnt,d=1)
        alljnts=cmds.ls(sl=1,type='joint')
        allNode=cmds.ls(sl=1)
        includegrp=u""

        for each_node in allNode:
            node_type = cmds.nodeType(each_node)
            if node_type not in ["joint", "transform"]:
                print 'Types that do not match <' + node_type + '> is a node which name is <' + each_node + '>'
                includegrp = includegrp + u"节点<" + each_node + u">不符合crd规范， 是一个<" + node_type + u">类型节点。\n"

        for jnt in alljnts:
            #jnt=alljnts[0]
            ps = cmds.listRelatives(jnt,p=1,pa=1)
            if ps:
                for p in ps:
                    if not cmds.nodeType(p) in ['joint', 'transform']:
                        print 'The type of the parent of the joint <'+jnt+'> is a transform which name is <'+p+'>'
                        includegrp=includegrp+u"骨骼<"+jnt+u">的父物体<"+p+u">是一个transform类型节点。\n"
        return includegrp

    def run_check(self):
        try:
            msg=self.check_skeleton_chain()
            return msg
        except:
            return traceback.format_exc()
    

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


