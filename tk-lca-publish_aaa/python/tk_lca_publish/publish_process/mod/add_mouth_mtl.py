# -*- coding:utf-8 -*-

import sys
import os
import pymel.core as pm
import maya.cmds as cmds
from proc.function_running_time import record_time


def has_custom_material(shape):
    """
    判断 Shape 是否已经绑定了非默认材质
    """
    sg_nodes = cmds.listConnections(
        shape + ".instObjGroups",
        source=False,
        destination=True,
        type="shadingEngine"
    ) or []

    for sg in sg_nodes:
        if sg != "initialShadingGroup":
            return True

    return False


def create_lambert(shader_name, color):
    """
    创建（或获取）Lambert 材质，并返回 Shading Group
    """

    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode(
            "lambert",
            asShader=True,
            name=shader_name
        )

        cmds.setAttr(
            shader + ".color",
            color[0], color[1], color[2],
            type="double3"
        )
    else:
        shader = shader_name

    sg = cmds.listConnections(shader + ".outColor", type="shadingEngine")

    if sg:
        sg = sg[0]
    else:
        sg = cmds.sets(
            renderable=True,
            noSurfaceShader=True,
            empty=True,
            name=shader + "SG"
        )

        cmds.connectAttr(
            shader + ".outColor",
            sg + ".surfaceShader",
            force=True
        )

    return shader, sg


def apply_mouth_colors():

    if not cmds.objExists("mouth_grp"):
        cmds.warning(u"未找到 mouth_grp")
        return

    mesh_shapes = cmds.ls(
        "mouth_grp",
        dag=True,
        long=True,
        type="mesh"
    ) or []

    if not mesh_shapes:
        cmds.warning(u"mouth_grp 下没有 Mesh")
        return

    # 创建材质
    _, tooth_sg = create_lambert(
        "Tooth_White_Mat",
        (1.0, 1.0, 1.0)
    )

    _, gum_sg = create_lambert(
        "Gums_Pink_Mat",
        (0.95, 0.55, 0.65)
    )

    assign_count = 0
    skip_count = 0

    for shape in mesh_shapes:

        # 已有材质则跳过
        if has_custom_material(shape):
            print(u"跳过（已有材质）：{}".format(shape))
            skip_count += 1
            continue

        transform = cmds.listRelatives(
            shape,
            parent=True,
            fullPath=True
        )[0]

        name = transform.lower()

        if "teeth" in name:
            cmds.sets(shape, e=True, forceElement=tooth_sg)
            print(u"牙齿赋白色材质：{}".format(transform))
        else:
            cmds.sets(shape, e=True, forceElement=gum_sg)
            print(u"口腔赋粉色材质：{}".format(transform))

        assign_count += 1

    cmds.select(clear=True)

    print("=" * 50)
    print(u"完成")
    print(u"新增材质：{}".format(assign_count))
    print(u"跳过已有材质：{}".format(skip_count))
    print("=" * 50)


# All publish process will use StdProcess as the class name.
class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"mod 给chr类型的资产，自动给口腔颜色"
        self.description = u"mod 给chr类型的资产，自动给口腔颜色"
        return

    @record_time(__file__)
    def proceed(self):
        asset = self.dialog.sg.find_one("Asset", [['project', 'is', self.dialog.project], ['code', 'is', self.dialog.entity['name']]], ['id', 'tags', 'sg_diffculty2', 'sg_asset_type'])
        if asset.get('sg_asset_type') != 'chr':
            return ''

        apply_mouth_colors()
        return ''

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description


