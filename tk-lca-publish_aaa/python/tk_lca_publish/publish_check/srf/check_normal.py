# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu xiaoyu
#
# Date: 2024.10
#
# Description: Check shtogun data
#
############################################

import traceback
import NodegraphAPI as ngapi
# All system check classes will use StdCheck as the class name.


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查normal贴图是否包涵  normal  字段。"
        self.description = u"检查normal贴图是否包涵  normal  字段。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def __get_upstream_image_nodes(self, node, visited=None):
        if visited is None:
            visited = []
        if node in visited:
            return visited
        if node.getParameter('nodeType') and node.getParameter('nodeType').getValue(0) == 'image':
            visited.append(node)
        input_ports = node.getInputPorts()
        for port in input_ports:
            connected_ports = port.getConnectedPorts()
            for connected_port in connected_ports:
                upstream_node = connected_port.getNode()
                self.__get_upstream_image_nodes(upstream_node, visited)
        return visited

    def check_normal(self):
        error_normal_tx = []
        normal_nodes_list = []
        arnold_shading_nodes_list = ngapi.GetAllNodesByType('ArnoldShadingNode')
        for node in arnold_shading_nodes_list:
            if node.getParameter('nodeType').getValue(0) == 'normal_map':
                normal_nodes_list.append(node)
        normal_map_nodes = []
        for node in normal_nodes_list:
            d_nodes = self.__get_upstream_image_nodes(node, visited=None)
            normal_map_nodes.extend(d_nodes)
        for normal_map_node in normal_map_nodes:
            normal_map = normal_map_node.getParameter('parameters.filename.value').getValue(0)
            if 'normal' not in normal_map:
                error_normal_tx.append(normal_map_node.getName())
        return error_normal_tx

    def run_check(self):
        try:

            check_normal = self.check_normal()
            if check_normal:
                return u"以下节点normal贴图命名不规范\n'" + "\n".join(check_normal)
            return ''
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


