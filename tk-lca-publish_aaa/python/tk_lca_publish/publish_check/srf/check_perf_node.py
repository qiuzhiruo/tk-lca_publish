# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Guan ZeJie
#
# Date: 2023.11
#
# Description: Check texture name and path
#
############################################

import traceback
import NodegraphAPI


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查noise节点是否有锁定perf。"
        self.description = u"检查noise节点是否有锁定perf。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            noise_node_name = ["MayaNoise", "MayaVolumeNoise", "camera_projection", "car_paint", "cell_noise",
                               "flakes", "lc_crazy_snow", "lc_noise_fractal", "lc_triplanar", "lc_triplanar3d",
                               "noise", "osl", "triplanar", "uv_projection"]
            merge_node = NodegraphAPI.GetAllNodesByType("Merge", includeDeleted=False)
            srf_mtl_merge_list = []
            for node in merge_node:
                if 'srf_mtl_Merge' == node.getName():
                    srf_mtl_merge_list = []
                    srf_mtl_merge_list.append(node)
                    break
                if 'srf_mtl_Merge' in node.getName():
                    srf_mtl_merge_list.append(node)

            if srf_mtl_merge_list:
                srf_mtl_merge = srf_mtl_merge_list[0]
            else:
                srf_mtl_merge = NodegraphAPI.GetNode('srf_mtl_Merge')

            mtl_node_list = []
            node_port = srf_mtl_merge.getInputPorts()

            # 第归获取所有的材质组节点
            temp_node_list = []
            while node_port:
                node = node_port.pop()
                connect_port = node.getConnectedPort(0)
                if not connect_port:
                    continue
                connect_node = connect_port.getNode()
                if not connect_node:
                    continue
                if connect_node.getType() == "Group":
                    mtl_node_list.append(connect_node)
                sub_input_ports = connect_node.getInputPorts()
                if sub_input_ports:
                    if sub_input_ports not in temp_node_list:
                        temp_node_list.append(sub_input_ports)
                        node_port.extend(sub_input_ports)
            mtl_node = list(set(mtl_node_list))

            perf_node = []
            for m_node in mtl_node:
                children = m_node.getChildren()
                for child in children:
                    if child.getType() == "ArnoldShadingNode":
                        if child.getParameter('nodeType').getValue(0) in noise_node_name:
                            perf_node.append(child)

            if perf_node:
                attribute_copy = NodegraphAPI.GetAllNodesByType("AttributeCopy")
                if attribute_copy:
                    for attr_node in attribute_copy:
                        is_from_root = attr_node.getParameter('fromRoot').getValue(0) == "/root/world/geo/assets" or attr_node.getParameter('fromRoot').getValue(0) == "/root/world/geo" or attr_node.getParameter('fromRoot').getValue(0) == "/root/world"
                        is_to_attr = attr_node.getParameter('toAttr').getValue(0) == "geometry.point.Pref"
                        is_from_attr = attr_node.getParameter('fromAttr').getValue(0) == "geometry.point.P"
                        is_to_root = attr_node.getParameter('toRoot').getValue(0) == "/root/world/geo/assets" or attr_node.getParameter('toRoot').getValue(0) == "/root/world/geo" or attr_node.getParameter('toRoot').getValue(0) == "/root/world"
                        if is_from_root and is_to_attr and is_from_attr and is_to_root:
                            return ""
                        else:
                            return u"文件里有需要锁perf的节点请添加AttributeCopy节点"
                else:
                    return u"文件里有需要锁perf的节点请添加AttributeCopy节点"

            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            dot = NodegraphAPI.GetNode('AssetInDot')
            if not dot:
                return u"修复失败，请手动添加"
            output = dot.getOutputPorts()[0]
            if not output:
                return u"修复失败，请手动添加"
            out_port = ""
            out_port_node = NodegraphAPI.GetNode('polyToSubdi_OpScript')
            if out_port_node:
                out_port = out_port_node.getInputPorts()[0]
            connected_ports = output.getConnectedPorts()
            if connected_ports:
                for node in connected_ports:
                    if node.getNode().getName() != "BakeDot":
                        out_port = node
                        break

            if not out_port:
                return u"修复失败，请手动添加"

            pos = NodegraphAPI.GetNodePosition(dot)
            down_pos = NodegraphAPI.GetNodePosition(out_port.getNode())
            new_pos = (pos[0], (down_pos[1] - pos[1]) / 2 + pos[1])
            new_node = NodegraphAPI.CreateNode("AttributeCopy", parent=NodegraphAPI.GetRootNode())
            new_node.getParameter('fromRoot').setValue("/root/world/geo/assets", 0)
            new_node.getParameter('fromAttr').setValue("geometry.point.P", 0)
            new_node.getParameter('toRoot').setValue("/root/world/geo/assets", 0)
            new_node.getParameter('toAttr').setValue("geometry.point.Pref", 0)
            NodegraphAPI.SetNodePosition(new_node, new_pos)

            for port in new_node.getInputPorts():
                output.connect(port)

            node_out_port = new_node.getOutputPorts()[0]
            node_out_port.connect(out_port)
            return ""


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