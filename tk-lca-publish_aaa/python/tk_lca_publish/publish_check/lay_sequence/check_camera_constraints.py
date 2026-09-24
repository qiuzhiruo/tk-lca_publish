# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import os
import traceback

import pymel.core as pm

import lay.lca_camera_lock.functions as functions_cl
reload(functions_cl)
import proc.check_camera_constraints as pccc
reload(pccc)


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否有约束到摄像机的物体。"
        self.description = u"由于摄像机可能输出并重新reference回来，所有以摄像机为目标的约束会失效，因此有约束到相机的物体不能通过检查。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            self.constrained_nodes = pccc.get_constrained_nodes()
            
            if self.constrained_nodes:
                pm.select(self.constrained_nodes)
                self.dialog.print_log(str(self.constrained_nodes))

                nodes_str = ''
                for i in self.constrained_nodes:
                    print i
                    nodes_str += str(i) + '\n'

                # nodes_str = '\n'.join(i.name() for i in self.constrained_nodes)
                return u'当前选中的节点约束到了摄像机，需要艺术家手动修改:\n%s' % nodes_str
            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
