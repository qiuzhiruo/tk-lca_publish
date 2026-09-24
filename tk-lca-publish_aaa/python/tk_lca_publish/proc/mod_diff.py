# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.02
#
############################################


from xml.etree import ElementTree
import hashlib
import re

class Mod_Diff():
    
    def __init__(self):
        self.l_moved = []
        self.l_missing = []
        self.l_new = []
        self.l_topology_changed = []
        return


    def xml_to_dict(self, mesh_xml,root_node='|master|poly|hi|'):
        d_meshes = {}
        l_order = []
        tree = ElementTree.parse(mesh_xml)
        root = tree.getroot()
        l_meshes = root.getiterator("mesh")
        for mesh in l_meshes:
            full_path = mesh.attrib['name']
            if not root_node in full_path:
                continue
            mesh_name = full_path.split('|')[-1]
            topology = mesh.attrib['topology']
            d_meshes[mesh_name] = {'path': full_path, 'topology':topology}
            l_order.append(mesh_name)
        return d_meshes, l_order


    def parse_xml(self, mesh_xml, root_node='|master|poly|hi', ignore_deform=False):
        import pymel.core as pm
        import maya.api.OpenMaya as om

        d_old_meshes, l_old_order = self.xml_to_dict(mesh_xml,root_node=root_node)

        d_new_meshes = {}
        l_new_mesh = pm.listRelatives(root_node, ad=True, type='mesh', noIntermediate=True)
        for i, mesh in enumerate(l_new_mesh):
            mesh_name = mesh.name().split('|')[-1]
            if ignore_deform:
                mesh_name = re.sub('Deformed$', '', mesh_name)
            d_new_meshes[mesh_name] = ''
            if not d_old_meshes.has_key(mesh_name):
                self.l_new.append(mesh_name)
            else:
                full_path = mesh.fullPath()
                full_path_name = full_path
                if ignore_deform:
                    full_path_name = re.sub('Deformed$','', full_path)

                if full_path_name != d_old_meshes[mesh_name]['path']:
                    self.l_moved.append(mesh_name)

                sl = om.MSelectionList()
                sl.add(full_path)
                mesh_dag = sl.getDagPath(0)
                mesh_mfn = om.MFnMesh(mesh_dag)
                v = mesh_mfn.getVertices()
                v_str0 = '[' + ', '.join([str(i) for i in v[0]]) + ']'
                v_str1 = '[' + ', '.join([str(i) for i in v[1]]) + ']'
                topology = hashlib.md5( v_str0 + ' ' + v_str1).hexdigest()
                if topology != d_old_meshes[mesh_name]['topology']:
                    self.l_topology_changed.append(mesh_name)

        for mesh_name in d_old_meshes.keys():
            if not d_new_meshes.has_key(mesh_name):
                self.l_missing.append(mesh_name)

        return


    def diff_xml(self, mesh_xml_old, mesh_xml_new):
        d_old_meshes, l_old_order = self.xml_to_dict(mesh_xml_old)
        d_new_meshes, l_new_order = self.xml_to_dict(mesh_xml_new)        

        for mesh_name in d_new_meshes.keys():
            if not d_old_meshes.has_key(mesh_name):
                self.l_new.append(mesh_name)
            else:
                if d_old_meshes[mesh_name]['path'] != d_new_meshes[mesh_name]['path']:
                    self.l_moved.append(mesh_name)
                if d_old_meshes[mesh_name]['topology'] != d_new_meshes[mesh_name]['topology']:
                    self.l_topology_changed.append(mesh_name)

        for mesh_name in d_old_meshes.keys():
            if not d_new_meshes.has_key(mesh_name):
                self.l_missing.append(mesh_name)

        return
