# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import traceback

import os
import re
import pymel.core as pm

from proc.function_running_time import record_time


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查非reference几何体信息。"
        self.description = u"scene资产|master|asb 组下允许有自定义的组，但不可以有非reference几何体信息，不可以与|master之外的物体有约束关系."
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        try:
            asb = pm.PyNode('|master|asb')
            l_trans = pm.listRelatives(asb, ad=True)

            l_geo = []
            l_outside = []
            for trans in l_trans:
                if pm.referenceQuery( trans, isNodeReferenced=True ):
                    continue

                #exclude constrains' nodes from rig under master
                if 'Constraint' in trans.type():
                    for j in list(set([i[1] for i in pm.listConnections(trans, c=True, scn=True) if len(i)>1])):
                        if not j.isChildOf(asb):
                            l_outside.append(j.name())
                    continue

                if trans.type() != 'transform':
                    l_geo.append(trans.name())

            if len(l_outside)>0:
                pm.select( clear=True )
                for i in l_outside:
                    j = pm.listRelatives(i,p=True,pa=True,type='transform')
                    if len(j)>0:
                        pm.select(j, add=True)
                return u'发现master以外的物体和内部发生约束关系：\n' + '\n'.join(l_outside)

            if len(l_geo)>0:
                pm.select( clear=True )
                for i in l_geo:
                    j = pm.listRelatives(i,p=True,pa=True,type='transform')
                    if len(j)>0:
                        pm.select(j, add=True)
                return u'发现非reference物体：\n' + '\n'.join(l_geo)

            return ""

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


