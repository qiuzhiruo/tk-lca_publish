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
import maya.cmds as cmds

import production.mayautils as mutils


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查master|poly|hi组下模型的nameSpace名称是否统一。"
        self.description = u"资产的master|poly|hi组下，不能存在命名空间不统一的模型节点（主要是意外复制操作导致），以免AbcExport stripNamespace后命名冲突导致输出失败"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            self.invalid_nodes = []
            higroups = cmds.ls('master|poly|hi', recursive=True) or list()
            for hi in mutils.progressIter(higroups,
                                          status=self.get_check_name(),
                                          isInterruptable=False):
                ns = ':'.join(hi.split(':')[:-1]) + ':'
                if ns == ':':
                    continue

                children = cmds.listRelatives(hi, allDescendents=True, path=True, type=('mesh'))
                if not children:
                    continue

                transforms = cmds.listRelatives(children, parent=True)

                invalid = [i for i in transforms if not i.startswith(ns)]
                if invalid:
                    self.invalid_nodes.extend(invalid)

            if self.invalid_nodes:
                return u'发现命名空间不统一的节点：' + ', '.join(self.invalid_nodes)

            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            for i in self.invalid_nodes:
                if cmds.objExists(i):
                    cmds.delete(i)

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

