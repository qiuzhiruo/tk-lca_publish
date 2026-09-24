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
import maya.api.OpenMaya as om
from proc.function_running_time import record_time


# All publish process will use StdProcess as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"记录模型mesh信息。"
        self.description = u"将模型的mesh层级结构，名称，点线面数记录为publish比对做准备。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
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
    def run_check(self):
        try:

            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                node_name = self.dialog.d_assets_info[asset_name]['node_name']

                # make a master if necessary
                if self.dialog.d_assets_info[asset_name]['parent']:
                    pm.parent(root, world=True)

                if node_name != 'master':
                    root.rename('master')



                mesh_xml = os.path.join(os.path.dirname(pm.system.sceneName()),'mesh.xml')
                
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
                try:
                    os.chmod(mesh_xml,0777)
                except:
                    pass

                # recovery root node
                if self.dialog.d_assets_info[asset_name]['parent']:
                    pm.parent(root, self.dialog.d_assets_info[asset_name]['parent'])

                if node_name != 'master':
                    root.rename(node_name)

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        try:
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
