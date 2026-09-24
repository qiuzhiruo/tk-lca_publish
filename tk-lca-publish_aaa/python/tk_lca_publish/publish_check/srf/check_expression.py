# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Guan ZeJie
#
# Date: 2023.03
#
# Description: Check texture name and path
#
############################################

import traceback
import NodegraphAPI
import os
import re


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查表达式书写规范。"
        self.description = u"检查表达式书写规范。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def get_attr_list(self, attr_list):
        attr_note_list = []
        attribute_list = attr_list
        while attribute_list:
            node = attribute_list.pop()
            if node.getType() == 'group' or node.getType() == 'numberArray':
                attribute_list.extend(node.getChildren())
            elif node.getType() == 'stringArray':
                pass
            else:
                if node.getName():
                    if node.getExpression() and node.isExpression():
                        attr_note_list.append(node.getExpression())
        return attr_note_list

    def run_check(self):
        try:
            l_NetworkMaterial = []
            expression_list = []
            all_NetworkMaterial = NodegraphAPI.GetAllNodesByType('NetworkMaterial')
            for node in all_NetworkMaterial:
                nodeName = node.getParameter('name').getValue(0)
                if nodeName[-16:] == '_NetworkMaterial' and NodegraphAPI.GetNode(nodeName):
                    l_NetworkMaterial.append(node)

            for NetworkMaterial in l_NetworkMaterial:
                node_list = NetworkMaterial.getParent().getChildren()
                for node in node_list:
                    parameters = node.getParameters().getChild('parameters')
                    if parameters and parameters.getChildren():
                        attr_list = self.get_attr_list(parameters.getChildren())
                        if attr_list:
                            expression_list.append([node.getName(), attr_list])
            error_list = []
            for script_note in expression_list:
                for note in script_note[1]:
                    match = re.match(r"[^\w\s(%/.'\"]", note)
                    if match:
                        error_list.append(script_note[0])
            if error_list:
                return u"节点的表达式书写不符合规范"+u"  ".join(error_list) + u"请使用srfFinalize工具重新检查文件"

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