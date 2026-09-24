# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.12
#
# Description: As the description shows below
#
############################################

import traceback
import pymel.core as pm

import production.mayautils as mutils
import ani.lca_asset_switch.functions as functions_as


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否有角色资产是Cache形态"
        self.description = u"在提交下游前，需要将之前转换成Cache的资产替换回绑定。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            self.caches_to_switch = []
            caches = pm.ls(exactType='gpuCache')
            for cache in mutils.progressIter(caches):
                cache = pm.nt.GpuCache(cache)
                if cache.hasAttr(functions_as.ATTR_SOURCE_REF):
                    self.caches_to_switch.append(cache)

            if self.caches_to_switch:
                pm.select(self.caches_to_switch)
                nodes_str = '\n'.join(i.name() for i in self.caches_to_switch)
                return u'当前选中的GPU Cache是角色资产，需要切换回绑定后提交:\n%s'%nodes_str
            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        self.run_check()
        if self.caches_to_switch:
            functions_as.back_to_reference(*self.caches_to_switch)
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
