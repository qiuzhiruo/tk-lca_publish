# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2020.06
#
# Description: 
#
############################################

import traceback
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 Maya 文件中的 script 节点"
        self.description = u"检查场景文件中是否有 sceneConfigurationScriptNode 之外的节点"
        self.auto_fix = True
        self.duty = u"TD/艺术家本人。"
        return

    def run_check(self):

        try:
            l_script_nodes = []
            for n in pm.ls(type='script'):
                node_name = n.name().strip('0123456789')
                if node_name not in ['sceneConfigurationScriptNode', 'td_name_check',
                                    'xgenGlobals', 'IGPUCS', '_sceneConfigurationScriptNode']:
                    l_script_nodes.append(n.name())

            if len(l_script_nodes) > 0:
                return u'发现 script 节点:\n\t' + '\n\t'.join(l_script_nodes)

            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            l_script_nodes = []
            for n in pm.ls(type='script'):
                if n.name() != 'sceneConfigurationScriptNode':
                    l_script_nodes.append(n.name())

            if len(l_script_nodes) > 0:
                pm.delete(l_script_nodes)
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
