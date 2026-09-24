# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.08
#
# Description: As the description shows below
#
############################################

import os
import traceback

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"清理 layout_safeareaShape 节点。"
        self.description = u"该节会导致 Linux 农场上输出 cache 过程崩溃，需要清理掉。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            import pymel.core as pm
            l_nodes = pm.ls(type="spReticleLoc")

            if len(l_nodes) > 0:
                return u"发现 safearea 节点: " + ', '.join([n.name() for n in l_nodes])

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        try:
            import pymel.core as pm
            l_nodes = pm.ls(type="spReticleLoc")

            for n in l_nodes:
                p = pm.listRelatives(n, parent=True)
                pm.delete(p)
            
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


