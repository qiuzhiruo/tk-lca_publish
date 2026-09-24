# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Guan ZeJie
#
# Date: 20236.08
#
# Description: Check shtogun data
#
############################################

import traceback
from Katana import NodegraphAPI, Nodes3DAPI
import os


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查custom shader的贴图路径。"
        self.description = u"检查custom shader的贴图路径。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def get_scene_graph(self, producer):
        mesh_list = []
        stack = [producer]
        while stack:
            child = stack.pop()
            children = child.iterChildren()
            if child.getType() == "polymesh" or child.getType() == "subdmesh":
                mesh_list.append(child)
            stack.extend(children)
        return mesh_list

    def run_check(self):
        try:
            self.error_group = []
            AssetIn_node = NodegraphAPI.GetNode('AssetXmlIn_Lc')
            if not AssetIn_node:
                for group_node in NodegraphAPI.GetAllNodesByType('Group'):
                    if 'AssetXmlIn_Lc' in group_node:
                        AssetIn_node = group_node
                        break
            render_settings_node = NodegraphAPI.GetNode('RenderSettings')
            if not render_settings_node:
                return u'没找到RenderSettings节点'
            NodegraphAPI.SetNodeEdited(render_settings_node, 1, 1)
            NodegraphAPI.SetNodeViewed(render_settings_node, 1, 1)
            rt_path = AssetIn_node.getParameter('user.location.name').getValue(0)
            root = Nodes3DAPI.GetGeometryProducer()
            producer = root.getProducerByPath(rt_path + '/master/poly')
            all_producers = []
            if producer:
                all_producers = self.get_scene_graph(producer)
            if all_producers:
                for geo in all_producers:
                    material_data = []
                    if geo.getAttribute('materialAssign'):
                        if not geo.getAttribute('materialAssign').getData():
                            continue
                        else:
                            material_data = geo.getAttribute('materialAssign').getData()
                    else:
                        if geo.getGlobalAttribute('materialAssign'):
                            if not geo.getGlobalAttribute('materialAssign').getData():
                                continue
                            else:
                                material_data = geo.getGlobalAttribute('materialAssign').getData()
                        else:
                            continue
                    if not material_data:
                        continue

                    material_name = material_data[0].split('/')
                    if len(material_name) < 2:
                        continue
                    if 'NetworkMaterial' not in material_name[-1]:
                        continue
                    material_node = NodegraphAPI.GetNode(material_name[-1])
                    if not material_node:
                        continue
                    mtl_group = material_node.getParent()
                    mtl_group_name = mtl_group.getName()
                    if not mtl_group.getParameter('user.customShader'):
                        continue
                    if mtl_group.getParameter('user.customShader').getValue(0) == 'Texture':
                        custom_texture = mtl_group.getParameter('user.customTexture').getValue(0)
                    else:
                        continue
                    uv_lst = []  # uv
                    if not geo.getAttribute('geometry.arbitrary.st.indexedValue'):
                        continue
                    temp_uv = geo.getAttribute('geometry.arbitrary.st.indexedValue').getData()
                    u_ = []
                    v_ = []
                    if temp_uv:
                        for i in range(int(len(temp_uv) / 2)):
                            u_.append(temp_uv[2 * i])
                            v_.append(temp_uv[2 * i + 1])
                        summed = set([int(a) + 1 + int(b) * 10 for a, b in zip(u_, v_)])
                        uv_lst = ["1%03d" % x for x in summed]
                    if not uv_lst:
                        continue
                    if "<udim>" in custom_texture:
                        for ud in uv_lst:
                            file_name = custom_texture.replace("<udim>", ud)
                            if not os.path.isfile(file_name):
                                self.error_group.append(mtl_group_name)
                                break
                    else:
                        if len(uv_lst) > 2:
                            self.error_group.append(mtl_group_name)

            if self.error_group:
                return u'custom shader的贴图路径错误，请应srfFinalize工具检查！'
            else:
                return u""

        except:
            return traceback.format_exc()

    def run_fix(self):
        try:
            for node_name in self.error_group:
                material_node = NodegraphAPI.GetNode(node_name)
                if not material_node:
                    continue
                if not material_node.getParameter('user.customShader'):
                    continue
                material_node.getParameter('user.customShader').setValue('None',0)
            return

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
