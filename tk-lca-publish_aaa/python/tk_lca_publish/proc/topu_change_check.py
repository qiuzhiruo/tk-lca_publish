# -*- coding:utf-8 -*-

########################################################################################
#
# Author: liangyue
#
# Date: 2026.06
#
# Description:
#
########################################################################################

# -*- coding:utf-8 -*-
import os
import hashlib
import pymel.core as pm
import maya.api.OpenMaya as om

from xml.dom import minidom
from xml.dom.minidom import Document


def _calc_mesh_topology(mesh):
    face_count = pm.polyEvaluate(mesh, face=True)
    if face_count == 0:
        return hashlib.md5(' ').hexdigest()

    sl = om.MSelectionList()
    sl.add(mesh.fullPath())   # ← 这里
    dag = sl.getDagPath(0)
    mfn = om.MFnMesh(dag)

    v = mfn.getVertices()
    v_str0 = '[' + ', '.join(map(str, v[0])) + ']'
    v_str1 = '[' + ', '.join(map(str, v[1])) + ']'

    return hashlib.md5((v_str0 + ' ' + v_str1)).hexdigest()


def _create_structure(doc, parent_elem, root_node):
    if not pm.objExists(root_node):
        return

    children = pm.listRelatives(
        root_node, children=True, fullPath=True
    ) or []
    children.sort()

    for node in children:
        node = pm.PyNode(node)

        if node.type() == 'transform':
            elem = doc.createElement('transform')
            elem.setAttribute('name', node.fullPath())
            parent_elem.appendChild(elem)
            _create_structure(doc, elem, node)

        elif node.type() == 'mesh' and not node.isIntermediate():
            topo = _calc_mesh_topology(node)

            elem = doc.createElement('mesh')
            elem.setAttribute('name', node.fullPath())
            #elem.setAttribute('vertex', str(pm.polyEvaluate(node, vertex=True)))
            elem.setAttribute('edge', str(pm.polyEvaluate(node, edge=True)))
            elem.setAttribute('face', str(pm.polyEvaluate(node, face=True)))
            elem.setAttribute('topology', topo)

            parent_elem.appendChild(elem)


# def generate_mesh_structure_xml(root_node, output_xml, lod_nodes=('hi', 'md', 'lo')):
#     """
#     根据 root_node 生成 mesh 结构 XML
#
#     :param root_node: '|master'
#     :param output_xml: '/path/to/mesh.xml'
#     :param lod_nodes: 默认 ('hi', 'md', 'lo')
#     """
#     if not pm.objExists(root_node):
#         raise RuntimeError('Root node does not exist: {}'.format(root_node))
#
#     doc = Document()
#
#     root_elem = doc.createElement('transform')
#     root_elem.setAttribute('name', root_node)
#     doc.appendChild(root_elem)
#
#     poly_path = root_node + '|poly'
#     if pm.objExists(poly_path):
#         poly_elem = doc.createElement('transform')
#         poly_elem.setAttribute('name', poly_path)
#         root_elem.appendChild(poly_elem)
#
#         for lod in lod_nodes:
#             lod_path = poly_path + '|' + lod
#             if pm.objExists(lod_path):
#                 lod_elem = doc.createElement('transform')
#                 lod_elem.setAttribute('name', lod_path)
#                 poly_elem.appendChild(lod_elem)
#                 _create_structure(doc, lod_elem, lod_path)
#
#     with open(output_xml, 'w') as f:
#         f.write(doc.toprettyxml(indent='    '))
#
#     try:
#         os.chmod(output_xml, 0o777)
#     except Exception:
#         pass
#
#     return output_xml


def generate_mesh_structure_xml(root_node, output_xml):
    """
    导出 root_node 组下所有 mesh 的拓扑结构 XML
    """
    if not pm.objExists(root_node):
        raise RuntimeError('Root node does not exist: {}'.format(root_node))

    doc = Document()

    root_elem = doc.createElement('transform')
    root_elem.setAttribute('name', pm.PyNode(root_node).fullPath())
    doc.appendChild(root_elem)

    #直接从 root_node 开始递归
    _create_structure(doc, root_elem, root_node)

    with open(output_xml, 'w') as f:
        f.write(doc.toprettyxml(indent='    '))

    try:
        os.chmod(output_xml, 0o777)
    except Exception:
        pass

    return output_xml


# --------------------------------------------------------------------------------------


# 对比两个xml进行检查

def _parse_mesh_topology(xml_file, root_grp=None, check_hair=False):
    """
    解析 xml，返回：

    {
        mesh_path: {
            'topology': xxx,
            #'vertex': xxx, don't need
            'edge': xxx,
            'face': xxx
        }
    }

    :param root_grp:
        None -> 全部解析

        '|master|shape|face_pass_grp'
            -> 只解析该层级下的 mesh
    """

    dom = minidom.parse(xml_file)
    meshes = dom.getElementsByTagName('mesh')

    data = {}

    root_grp = root_grp.rstrip('|') if root_grp else None

    for mesh in meshes:
        name = mesh.getAttribute('name')

        # 过滤指定组
        if root_grp:
            if name != root_grp and not name.startswith(root_grp + '|'):
                continue

        # face pass只检查毛发壳， 以 shell_ 开头的
        if check_hair and not name.split('|')[-1].startswith('shell_'):
            continue
        data[name] = {
            'topology': mesh.getAttribute('topology'),
            #'vertex': mesh.getAttribute('vertex'),
            'edge': mesh.getAttribute('edge'),
            'face': mesh.getAttribute('face'),
        }
    return data


def compare_mesh_topology_xml(old_xml, new_xml, old_grp=None, new_grp=None, check_hair=False):
    """
    对比两个 mesh topology xml

    :param old_grp:
        旧 xml 中指定比较的根组

    :param new_grp:
        新 xml 中指定比较的根组

    :return:

    {
        'topology_changed': [],
        'added': [],
        'removed': [],
        'detail': {}
    }
    """

    old_data = _parse_mesh_topology(old_xml, root_grp=old_grp, check_hair=check_hair)
    new_data = _parse_mesh_topology(new_xml, root_grp=new_grp, check_hair=check_hair)

    old_meshes = set(old_data.keys())
    new_meshes = set(new_data.keys())

    added = sorted(list(new_meshes - old_meshes))
    removed = sorted(list(old_meshes - new_meshes))

    topology_changed = []
    detail = {}

    common = old_meshes & new_meshes
    for mesh in common:
        if old_data[mesh]['topology'] != new_data[mesh]['topology']:
            topology_changed.append(mesh)
            detail[mesh] = {
                'old': old_data[mesh],
                'new': new_data[mesh]
            }

    return {
        'topology_changed': topology_changed,
        'added': added,
        'removed': removed,
        'detail': detail
    }


def get_mesh_topu(mesh_name, mesh_xml):
    r = ''
    dom = minidom.parse(mesh_xml)
    meshes = dom.getElementsByTagName('mesh')

    for mesh in meshes:
        name = mesh.getAttribute('name')
        if name == mesh_name:
            r = mesh.getAttribute('topology')
            break
    return r


'''
# 旧的xml

xml_path = '/mnt/work/shome/liangyue/test/maya/topu/mesh.xml' 
generate_mesh_structure_xml(
    root_node='|master|shape|face_pass_grp',
    output_xml=xml_path
)


# 新的xml

new_xml_path = '/mnt/work/shome/liangyue/test/maya/topu/new_mesh.xml' 
generate_mesh_structure_xml(
    root_node='|master|shape|face_pass_grp',
    output_xml=new_xml_path
)


# check topu
result = compare_mesh_topology_xml(
    old_xml=xml_path,
    new_xml=new_xml_path
)

print('Topo Changed:', result['topology_changed'])
print('Added:', result['added'])
print('Removed:', result['removed'])
'''

