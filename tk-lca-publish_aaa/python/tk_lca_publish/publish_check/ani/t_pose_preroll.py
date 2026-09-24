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
import ani.lca_t_pose.functions as functions

CHR_GROU = '|assets|chr'
T_ATTRS = ('translateX', 'translateY', 'translateZ',
           'rotateX', 'rotateY', 'rotateZ',
           'scaleX', 'scaleY', 'scaleZ')
T_IGNORE = ('global_ctrl', 'root_ctrl')
T_MODULES = ('arm', 'head', 'spine', 'leg', 'hand', 'foot', 'neck', 'shoulder', 'tail')


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查角色资产是否制作了T-Pose预留帧。"
        self.description = u"所有角色类型的资产，需要在950帧和980帧(起始帧是1001为例)设置T-Pose预留帧，方便CFX解算。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"

        shot = self.dialog.sg.find_one('Shot', [['id', 'is', self.dialog.entity['id']]], ['sg_cut_in', 'sg_ani_cut_in'])
        self.start_frame = shot['sg_cut_in']
        ani_cut_in = shot['sg_ani_cut_in']
        if ani_cut_in:
            self.start_frame = ani_cut_in
        return

    def run_check(self):
        result = ''
        try:
            t_start = self.start_frame - functions.REST_TIME - functions.TRANSITION_TIME
            t_end = self.start_frame - functions.REST_TIME
            self.invalid_ctrls = []
            chrs = cmds.listRelatives(CHR_GROU, children=True, path=True)
            if chrs:
                for c in chrs:
                    if not cmds.reference(c, q=True, inr=True):
                        continue

                    ns = ':'.join(c.split(':')[:-1])
                    asset_name = ''.join([i for i in ns.split(':')[-1] if not i.isdigit()])
                    task_info = self.dialog.sg.find_one('Task', [['entity', 'name_is', asset_name],
                                                                 ['step', 'name_is', 'cfx'],
                                                                 ['content', 'is', 'cloth']],
                                                        ['sg_status_list'])
                    if task_info and task_info['sg_status_list'] == 'omt':
                        continue

                    controls = cmds.ls('{}:*_ctrl'.format(ns), referencedNodes=True)
                    for ctrl in mutils.progressIter(controls, status=self.get_check_name(), isInterruptable=False):
                        if any(ctrl.endswith(i) for i in T_IGNORE):
                            continue

                        if not any(i in ctrl for i in T_MODULES):
                            continue

                        if ctrl in functions.CONTROLS_EXCLUDE:
                            continue

                        if not cmds.listConnections(ctrl, d=False, type='animCurve'):
                            continue

                        # ignore some special ctrls which can not animate t r s
                        if cmds.listAnimatable(ctrl) and not [a for a in cmds.listAnimatable(ctrl) if a.split('.')[-1] in T_ATTRS]:
                            continue

                        if not cmds.keyframe(ctrl, q=True, time=(t_start, t_start), keyframeCount=True) or \
                                not cmds.keyframe(ctrl, q=True, time=(t_end, t_end), keyframeCount=True):
                            self.invalid_ctrls.append(ctrl)

            if self.invalid_ctrls:
                cmds.select(self.invalid_ctrls)
                result = '这些控制器没有在{}帧和{}帧为T-Pose预留帧:\n{}'.format(t_start, t_end, ', '.join(self.invalid_ctrls))
        except:
            result = traceback.format_exc()

        return result

    def run_fix(self):
        '''Auto Fix'''
        # try:
        #     if self.invalid_nodes:
        #         cmds.select(self.invalid_nodes)
        #         functions.setup(self.start_frame)
        #         cmds.currentTime(self.t_frame)
        #     return ''
        # except:
        #     return traceback.format_exc()
        pass

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
