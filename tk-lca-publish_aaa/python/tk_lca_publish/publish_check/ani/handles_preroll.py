# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: wanghuan
#
# Date: 2014.11
#
# Description: see description below
#
############################################

import traceback
import os
import math
import maya.cmds as cmds

import production.mayautils as mutils

CHR_GROU = '|assets|chr'
HANDLES = 3
H_ATTRS = ('translateX', 'translateY', 'translateZ',
           'rotateX', 'rotateY', 'rotateZ',
           'scaleX', 'scaleY', 'scaleZ')

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产在手柄范围内是否制作了预留帧。"
        self.description = u"所有动画资产，需要在镜头正常制作范围外增加前后各3帧手柄帧，防止运动模糊出错。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            self.invalid_nodes = []
            shotInfo = self.dialog.sg.find_one('Shot', [['id', 'is', self.dialog.entity['id']]], ['sg_cut_in', 'sg_cut_out'])
            fStart = shotInfo['sg_cut_in']
            fEnd = shotInfo['sg_cut_out']
            fPre = fStart - HANDLES
            fPost = fEnd + HANDLES

            assets = cmds.listRelatives(CHR_GROU, children=True, path=True)
            assets = cmds.ls(assets, referencedNodes=True)
            for asset in assets:
                ns = ':'.join(asset.split(':')[:-1])
                controls = cmds.ls(ns+':*_ctrl', referencedNodes=True)
                for c in mutils.progressIter(controls,
                                             status=self.get_check_name(),
                                             isInterruptable=False):
                    for attr in H_ATTRS:
                        if not cmds.attributeQuery(attr, node=c, exists=True):
                            continue

                        if not cmds.attributeQuery(attr, node=c, keyable=True):
                            continue

                        if cmds.attributeQuery(attr, node=c, hidden=True):
                            continue

                        path = c+'.'+attr
                        if cmds.getAttr(path, lock=True):
                            continue

                        curves = cmds.listConnections(path, destination=False, type='animCurve')
                        if not curves:
                            continue

                        if cmds.referenceQuery(curves[0], isNodeReferenced=True):
                            continue

                        keys = cmds.keyframe(curves, query=True, valueChange=True)
                        keys = set(keys)
                        if len(keys) <= 1:
                            continue

                        firstKey = cmds.findKeyframe(curves, which='first')
                        lastKey = cmds.findKeyframe(curves, which='last')
                        preHandle = cmds.keyframe(curves, query=True, time=(fPre, fStart-1))
                        if firstKey > fPre or lastKey < fPost or not preHandle:
                            self.invalid_nodes.append(path)

            if self.invalid_nodes:
                cmds.select(self.invalid_nodes)
                return u'发现未制作手柄帧的曲线：\n' + ',\n'.join(self.invalid_nodes)

            return ''
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

