# -*- coding:utf-8 -*-

import hashlib
from xml.dom.minidom import Document
import pymel.core as pm
import maya.api.OpenMaya as om

class Mesh_XML():

    def __init__(self, mesh_xml):

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

        f = open(mesh_xml, 'w')
        f.write(self.doc.toprettyxml(indent = '    '))
        f.close()
        return

    def create_structure(self, root_elem, root_node):
        if not pm.objExists(root_node):
            return

        l_nodes = pm.listRelatives(root_node)
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


