# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Guan ZeJie
#
# Date: 2023.01
#
# Description: Check shtogun data
#
############################################

import traceback
import NodegraphAPI as ngapi


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"材质模板里的关键节点不可以随便改名字。"
        self.description = u"材质模板里的关键节点不可以随便改名字。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            error_node = []
            merge_node = ngapi.GetNode('Merge')
            global_settings_node = ngapi.GetNode('ArnoldGlobalSettings')
            channel_define_node = ngapi.GetNode('ArnoldOutputChannelDefine_Stack')
            render_settings_node = ngapi.GetNode('RenderSettings')

            if not merge_node:
                error_node.append('Merge')

            if error_node:
                return u"请查看Merge节点的命名是不是家里后缀，默认的名字是Merge"

            else:
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
