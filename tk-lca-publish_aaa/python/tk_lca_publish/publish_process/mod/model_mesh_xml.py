# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description: 
#
############################################

import os
import traceback
import hashlib
from xml.dom.minidom import Document
import pymel.core as pm
import json
import maya.api.OpenMaya as om
import maya.cmds as mc
from proc.function_running_time import record_time
from proc.topu_change_check import generate_mesh_structure_xml



# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录模型mesh信息, 初始posse数据, 导出shape信息。"
        self.description = u"将模型的mesh层级结构，名称，点线面数记录为下游组比对做准备。"
        return


    def create_structure(self, root_elem, root_node):
        if not pm.objExists(root_node):
            return

        l_nodes = pm.listRelatives(root_node)
        l_nodes.sort()
        for node in l_nodes:
            if node.type() == 'transform':
                trans = self.doc.createElement('transform')
                trans.setAttribute('name', node.fullPath())
                root_elem.appendChild(trans)
                self.create_structure(trans, node)
            elif node.type() == 'mesh' and (not node.isIntermediate()):
                if pm.polyEvaluate(node, face=True) == 0:
                    topology = hashlib.md5(' ').hexdigest()
                else:
                    sl = om.MSelectionList()
                    sl.add(node.fullPath())
                    mesh_dag = sl.getDagPath(0)
                    mesh_mfn = om.MFnMesh(mesh_dag)
                    v = mesh_mfn.getVertices()
                    v_str0 = '[' + ', '.join([str(i) for i in v[0]]) + ']'
                    v_str1 = '[' + ', '.join([str(i) for i in v[1]]) + ']'
                    topology = hashlib.md5( v_str0 + ' ' + v_str1).hexdigest()

                mesh = self.doc.createElement('mesh')
                mesh.setAttribute('name', node.fullPath())
                mesh.setAttribute('vertex', str(pm.polyEvaluate(node, vertex=True)))
                mesh.setAttribute('edge', str(pm.polyEvaluate(node, edge=True)))
                mesh.setAttribute('face', str(pm.polyEvaluate(node, face=True)))
                mesh.setAttribute('topology', topology)
                root_elem.appendChild(mesh)

        return

    @record_time(__file__)
    def proceed(self):
        try:

            for asset_name in self.dialog.d_assets_info.keys():
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                root = self.dialog.d_assets_info[asset_name]['node']
                node_name = self.dialog.d_assets_info[asset_name]['node_name']

                # make a master if necessary
                if self.dialog.d_assets_info[asset_name]['parent']:
                    pm.parent(root, world=True)

                if node_name != 'master':
                    root.rename('master')

                if pm.ls('|master|shape'):
                    shape_xml = version_dir + '/shape.xml'
                    generate_mesh_structure_xml('|master|shape', shape_xml)

                mesh_xml = version_dir + '/mesh.xml'
                self.doc = Document()
                master = self.doc.createElement('transform')
                master.setAttribute('name', '|master')
                self.doc.appendChild(master)
                poly = self.doc.createElement('transform')
                poly.setAttribute('name', '|master|poly')
                master.appendChild(poly)
                if pm.objExists('|master|poly|hi'):
                    res_node = self.doc.createElement('transform')
                    res_node.setAttribute('name', '|master|poly|hi')
                    poly.appendChild(res_node)
                    self.create_structure(res_node, '|master|poly|hi' )

                if pm.objExists('|master|poly|md'):
                    res_node = self.doc.createElement('transform')
                    res_node.setAttribute('name', '|master|poly|md')
                    poly.appendChild(res_node)
                    self.create_structure(res_node, '|master|poly|md' )

                if pm.objExists('|master|poly|lo'):
                    res_node = self.doc.createElement('transform')
                    res_node.setAttribute('name', '|master|poly|lo')
                    poly.appendChild(res_node)
                    self.create_structure(res_node, '|master|poly|lo' )

                f = open(mesh_xml, 'w')
                f.write(self.doc.toprettyxml(indent = '    '))
                f.close()

                # recovery root node
                if self.dialog.d_assets_info[asset_name]['parent']:
                    pm.parent(root, self.dialog.d_assets_info[asset_name]['parent'])

                if node_name != 'master':
                    root.rename(node_name)

            # 写出初始posse数据
            ctrl_list = [x for x in mc.ls('*_ctrl') if 'sec_ctrl' not in x and 'pri_ctrl' not in x]

            writ_list = []
            for ctrl in ctrl_list:
                a = mc.listAttr(ctrl, userDefined=1, unlocked=1, multi=0)
                if not a:
                    continue
                #b = list(set(a))
                c = mc.listAttr(ctrl, l=1) or []
                #attr_list = [item for item in b if item not in c]
                attr_list = set(a) - set(c)
                temp_list = []
                for attr in attr_list:
                    attr_name = '{}.{}'.format(ctrl, attr)
                    try:
                        if mc.getAttr(attr_name, type=True) == 'string':
                            continue
                        value = mc.getAttr(attr_name)
                    except:
                        continue
                    temp_list = [attr_name, value]
                    if temp_list == []:
                        continue
                    if temp_list not in writ_list:
                        writ_list.append(temp_list)
            # if mc.objExists('cloth_vis_ctrl.T_pose'):
            #     Tpose_value = mc.getAttr('cloth_vis_ctrl.T_pose')
            #     temp_list = ['cloth_vis_ctrl.T_pose', Tpose_value]
            #     if temp_list not in writ_list:
            #         writ_list.append(temp_list)

            json_path = version_dir + '/DefaultPose.json'
            with open(json_path, 'w') as f:
                json.dump(writ_list, f, indent=4)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


