# -*- coding:utf-8 -*-

########################################################################################
#
# Author: liangyue
#
# Date: 2026.09
#
# Description: 检查两个点之间多条边的问题
#
########################################################################################
import os
import json
import traceback
import pymel.core as pm
import maya.cmds as cmds
import maya.OpenMaya as om

import re
from proc.function_running_time import record_time


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查重复边。"
        self.description = u"检查两个点之间多条边的问题 。" \
                           u"\n修复方法：\n 1,直接删除边，删除不了， 需要手动删除面，然后重新生面 ， 最后重传一下点序（保持拓扑不变）\n " \
                           u"2,把有重复边的mesh 导出abc 再导进来,并重新给下材质 " \
                           u"\n 注： 该检查不可跳过，会导致拓扑不对， 会对下游cfx以及lgt有影响"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def get_shape_duplicate_edges(self, shape):
        """
        检查一个 mesh 中：
        同一对 vertex 之间是否存在多条 edge。

        Returns:
            [
                [edge1, edge2],
                [edge3, edge4, edge5],
            ]
        """

        if not cmds.objExists(shape):
            return []

        if cmds.nodeType(shape) != "mesh":
            return []

        sel = om.MSelectionList()
        sel.add(shape)

        dag_path = om.MDagPath()
        sel.getDagPath(0, dag_path)

        edge_map = {}

        edge_iter = om.MItMeshEdge(dag_path)

        while not edge_iter.isDone():

            edge_id = edge_iter.index()

            v1 = edge_iter.index(0)
            v2 = edge_iter.index(1)

            # 边方向无关
            # (10, 20) 和 (20, 10) 是同一对点
            if v1 > v2:
                v1, v2 = v2, v1

            key = (v1, v2)

            if key not in edge_map:
                edge_map[key] = []

            edge_map[key].append(edge_id)

            edge_iter.next()

        duplicate_edges = []

        for edge_ids in edge_map.values():

            if len(edge_ids) > 1:
                duplicate_edges.append([
                    "{}.e[{}]".format(shape, edge_id)
                    for edge_id in edge_ids
                ])

        return duplicate_edges

    def get_all_duplicate_edges(self, root="|master|poly|hi"):
        result = {}
        if not cmds.objExists(root):
            cmds.warning(u"节点不存在: {}".format(root))
            return result
        shapes = cmds.listRelatives(
            root,
            allDescendents=True,
            type="mesh",
            fullPath=True
        ) or []
        for shape in shapes:
            # 跳过 intermediate shape
            try:
                if cmds.getAttr(shape + ".intermediateObject"):
                    continue
            except:
                pass
            duplicate_edges = self.get_shape_duplicate_edges(shape)

            if duplicate_edges:
                result[shape] = duplicate_edges

        return result

    @record_time(__file__)
    def run_check(self):
        """
        check function
        @return: str (错误信息，如果通过则返回空字符串 '')
        """
        try:
            error_info = self.get_all_duplicate_edges()
            if error_info:
                edges = [
                    edge
                    for groups in error_info.values()
                    for group in groups
                    for edge in group
                ]

                if edges:
                    cmds.select(edges, r=True)
                else:
                    cmds.select(clear=True)

                msg_list = []

                for shape, groups in error_info.items():
                    msg_list.append(
                        u"模型存在重复边: {}".format(shape)
                    )

                    for index, edges in enumerate(groups, 1):
                        msg_list.append(
                            u"    第{}组: {}".format(
                                index,
                                u", ".join(edges)
                            )
                        )

                msg = u"\n".join(msg_list)
                return msg

            return ""

        except Exception as e:
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
