# -*- coding:utf-8 -*-

########################################################################################
#
# Author: liangyue
#
# Date: 2026.07
#
# Description: 获取材质信息的一些通用函数
#
########################################################################################
import os
import glob
import maya.cmds as cmds


def get_mesh_materials(mesh):
    # 获取mesh 上连接的材质球
    if cmds.nodeType(mesh) == 'transform':
        shapes = cmds.listRelatives(mesh, shapes=True, noIntermediate=True, fullPath=True) or []
        if not shapes:
            return []
        mesh = shapes[0]

    # 获取 shadingEngine
    sgs = cmds.listConnections(mesh, type='shadingEngine') or []

    materials = set()
    for sg in sgs:
        mats = cmds.listConnections(sg + '.surfaceShader', source=True, destination=False ) or []
        materials.update(mats)

    return list(materials)


def find_file_nodes(node):
    visited = set()
    result = []
    if node in visited:
        return

    visited.add(node)

    if cmds.nodeType(node) == 'file':
        result.append({
            'file_node': node,
            'file_path': cmds.getAttr(node + '.fileTextureName')
        })
        return

    inputs = cmds.listConnections(
        node,
        source=True,
        destination=False
    ) or []

    for input_node in inputs:
        find_file_nodes(input_node)


def get_texture_from_material(material, attr):
    """
    获取材质某个通道连接的贴图。

    Args:
        material (str): 材质球名称
        attr (str): 通道名称，例如：
            baseColor
            emissionColor
            transparency

    Returns:
        list:
            [
                {
                    "file_node": "file1",
                    "file_path": "/xxx/abc.exr"
                }
            ]
    """

    result = []
    material_attr = '{}.{}'.format(material, attr)
    if not cmds.objExists(material_attr):
        return result

    # 找到直接连接
    src_nodes = cmds.listConnections(material_attr, source=True, destination=False ) or []

    visited = set()

    for node in src_nodes:
        find_file_nodes(node)

    return result


def is_material_transparent(material):
    """
    判断材质是否存在透明效果。
    支持：
        lambert / blinn / phong 等：
            transparency
        surfaceShader：
            outTransparency
        aiStandardSurface：
            opacity
    """
    if not cmds.objExists(material):
        return False
    # Maya 普通材质lambert / blinn / phong...
    if cmds.attributeQuery('transparency', node=material, exists=True):
        try:
            value = cmds.getAttr(material + '.transparency')
            if value:
                # 一般返回 [(r, g, b)]
                value = value[0]
                if max(value) > 0:
                    return True
        except Exception:
            pass
    # surfaceShader
    if cmds.attributeQuery('outTransparency', node=material, exists=True):
        try:
            value = cmds.getAttr(material + '.outTransparency')
            if value:
                value = value[0]

                if max(value) > 0:
                    return True
        except Exception:
            pass
    # Arnold aiStandardSurface
    # opacity:
    #   1,1,1 = 完全不透明
    #   小于1 = 存在透明
    if cmds.attributeQuery('opacity', node=material, exists=True):
        try:
            value = cmds.getAttr(material + '.opacity')
            if value:
                value = value[0]

                if min(value) < 1:
                    return True
        except Exception:
            pass
    return False


def has_valid_texture(material):
    file_nodes = cmds.listConnections(material, type='file') or []

    for file_node in file_nodes:

        tex = cmds.getAttr(file_node + '.fileTextureName') or ''

        if not tex:
            continue

        tex = cmds.workspace(expandName=tex)

        if '<UDIM>' in tex or '<udim>' in tex:
            pattern = tex.replace('<UDIM>', '*').replace('<udim>', '*')
            if glob.glob(pattern):
                return True
        elif os.path.exists(tex):
            return True

    return False


def is_file_node_texture_exists(file_node):
    """
    判断 file 节点上的贴图是否真实存在

    Args:
        file_node (str): Maya file 节点

    Returns:
        bool
    """

    if not cmds.objExists(file_node):
        return False

    # 必须是 file 节点
    if cmds.nodeType(file_node) != "file":
        return False

    tex_path = cmds.getAttr(file_node + ".fileTextureName") or ""

    if not tex_path:
        return False

    # 展开 workspace 相对路径
    tex_path = cmds.workspace(expandName=tex_path)

    # UDIM
    if "<UDIM>" in tex_path or "<udim>" in tex_path:
        pattern = tex_path.replace("<UDIM>", "*").replace("<udim>", "*")
        return len(glob.glob(pattern)) > 0

    # 普通贴图
    return os.path.isfile(tex_path)
