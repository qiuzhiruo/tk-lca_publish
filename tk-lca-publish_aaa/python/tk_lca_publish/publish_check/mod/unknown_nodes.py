# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.09
#
# Description:
#
########################################################################################

import traceback
import pymel.core as pm
import maya.cmds as cmds
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查未知节点和未知插件"
        self.description = u"如果节点类型为 unknown, 需要在保存文件之前清理掉。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            if cmds.unknownPlugin(q=1, l=1):
                return u"发现未知插件: " + u'\n'.join(cmds.unknownPlugin(q=1, l=1))

            unknown_nodes = pm.ls(type='unknown')
            if unknown_nodes:
                return u"发现不明类型节点: " + u' '.join([n.name() for n in unknown_nodes])
            foster_parent_nodes = pm.ls(type='fosterParent')
            if foster_parent_nodes:
                pm.select(foster_parent_nodes)
                return u"发现fosterparent类型节点: " + u' '.join([n.name() for n in foster_parent_nodes])
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            unknown_nodes = pm.ls(type='unknown')
            if unknown_nodes:
                pm.delete(unknown_nodes)

            if cmds.unknownPlugin(q=1, l=1):
                for plugin in cmds.unknownPlugin(q=1, l=1):
                    cmds.unknownPlugin(plugin, remove=True)
            foster_parent_nodes = cmds.ls(type='fosterParent')
            if foster_parent_nodes:
                self.convert_foster_parent_to_mesh(foster_parent_nodes)
            return ''
        except:
            return traceback.format_exc()

    def convert_foster_parent_to_mesh(self,foster_parent_nodes):
        for foster_parent_node in foster_parent_nodes:
            # 获取fosterParent节点的输入连接
            input_plugs = cmds.listConnections(foster_parent_node, source=True, destination=False, plugs=True)

            mesh_node = cmds.createNode("mesh")
            if input_plugs:
                for input_plug in input_plugs:
                    # 获取连接的输出节点和属性
                    output_plug = cmds.connectionInfo(input_plug, sourceFromDestination=True)

                    # 断开fosterParent节点的输入连接
                    cmds.disconnectAttr(output_plug, input_plug)

                    # 将输出连接到新的mesh节点
                    cmds.connectAttr(output_plug, "{}.inMesh".format(mesh_node))
            p = cmds.listRelatives(foster_parent_node, parent=True)[0]
            cmds.parent(mesh_node, p)
            # 删除fosterParent节点
            cmds.delete(foster_parent_node)

            transform_node = cmds.listRelatives(mesh_node, parent=True, type='transform')
            # 重命名新transform_node节点为原始fosterParent节点的名称
            cmds.rename(transform_node[0], foster_parent_node)

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
