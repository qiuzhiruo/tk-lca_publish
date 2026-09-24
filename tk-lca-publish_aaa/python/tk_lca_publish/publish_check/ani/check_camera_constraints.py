# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.09
#
# Description: As the description shows below
#
############################################

import traceback
import pymel.core as pm

from proc import check_camera_constraints
reload(check_camera_constraints)


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否有约束到摄像机的物体。"
        self.description = u"由于摄像机可能输出并重新reference回来，所有以摄像机为目标的约束会失效，需要先bake results。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            constrained_nodes = check_camera_constraints.get_constrained_nodes()
            if constrained_nodes:
                pm.select(constrained_nodes)
                nodes_str = '\n'.join(i.name() for i in constrained_nodes)
                return u'当前选中的节点约束到了摄像机，需要Bake后提交:\n%s'%nodes_str
            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        constrained_nodes = check_camera_constraints.get_constrained_nodes()
        if constrained_nodes:
            f_start = pm.playbackOptions(query=True, min=True) - 1
            f_end = pm.playbackOptions(query=True, max=True) + 1
            pm.bakeResults(constrained_nodes, time=(f_start, f_end))
            pm.filterCurve(constrained_nodes)
            pm.keyTangent(constrained_nodes,
                          inTangentType='spline',
                          outTangentType='spline')
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
