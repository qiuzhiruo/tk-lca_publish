# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Cheng Shun
#
# Date: 2018.04
#
# Description: As the description shows below
#
############################################

import os
import traceback
import glob
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 Yeti 中的自定义属性是否带有 lca_ 前缀"
        self.description = u"如标题"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return


    def run_check(self):
        DEFAULT_USER_DATA=['vparamcoord','uparamcoord','curve_id','Cd','Alpha','width',\
            'strandu', 'feather_param', 'feather_part', 'feather_s', 'feather_t', 'parent_t', 'parent_s', 'patent_id',\
            'huzi','jiemao','huxu','Pref']
        try:
            l_errs = []
            for yeti_node in pm.ls(type = 'pgYetiMaya'):
                for attr_node in pm.pgYetiGraph(yeti_node, listNodes=1, type='attribute'):
                    add_mapping_attr = pm.pgYetiGraph(yeti_node, node=attr_node, param='addMapping', getParamValue=True)
                    if not add_mapping_attr:
                        continue
                    mapping_attr = pm.pgYetiGraph(yeti_node, node=attr_node, param='mapping', getParamValue=True)
                    if not mapping_attr.startswith('lca_') and not mapping_attr in DEFAULT_USER_DATA:
                        l_errs.append(' '.join([u'自定义属性名需要修正:', yeti_node.nodeName(), attr_node, mapping_attr]))

            return '\n'.join(l_errs)
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


