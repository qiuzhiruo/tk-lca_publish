# -*- coding:utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import json
import os
import traceback
from proc.function_running_time import record_time


def get_arnold_data():
    '''

    @return:
        {
        '|master|poly|hi|mesh_grp|yumao|yumao_3|yumao_3Shape':
            ['yumao_3Shape.aiVisibleInDiffuseReflection':True,
             'yumao_3Shape.aiDispHeight':1.0,
             ...
             ]
        '|master|poly|hi|mesh_grp|toushi_grp|huawen_25|huawen_25Shape':
            [...],
        }
    '''
    cmds.select(cl=True)
    mesh_name_list = cmds.ls(type="mesh")
    mesh_info = {}
    for mesh_n in mesh_name_list:
        mesh = str(mesh_n)
        arnold_sub_data = {}
        aiOpaque = mesh + ".aiOpaque"
        try:
            cmds.getAttr(aiOpaque)
        except:
            return mesh_info
        arnold_sub_data[aiOpaque] = cmds.getAttr(aiOpaque)

        aiMatte = mesh + ".aiMatte"
        arnold_sub_data[aiMatte] = cmds.getAttr(aiMatte)

        # visibility
        primaryVisibility = mesh + ".primaryVisibility"
        arnold_sub_data[primaryVisibility] = cmds.getAttr(primaryVisibility)

        castsShadows = mesh + ".castsShadows"
        arnold_sub_data[castsShadows] = cmds.getAttr(castsShadows)

        DiffuseReflection = mesh + ".aiVisibleInDiffuseReflection"
        arnold_sub_data[DiffuseReflection] = cmds.getAttr(DiffuseReflection)

        SpecularReflection = mesh + ".aiVisibleInSpecularReflection"
        arnold_sub_data[SpecularReflection] = cmds.getAttr(SpecularReflection)

        DiffuseTransmission = mesh + ".aiVisibleInDiffuseTransmission"
        arnold_sub_data[DiffuseTransmission] = cmds.getAttr(DiffuseTransmission)

        SpecularTransmission = mesh + ".aiVisibleInSpecularTransmission"
        arnold_sub_data[SpecularTransmission] = cmds.getAttr(SpecularTransmission)

        aiVisibleInVolume = mesh + ".aiVisibleInVolume"
        arnold_sub_data[aiVisibleInVolume] = cmds.getAttr(aiVisibleInVolume)

        aiSelfShadows = mesh + ".aiSelfShadows"
        arnold_sub_data[aiSelfShadows] = cmds.getAttr(aiSelfShadows)

        trace_sets = mesh + ".trace_sets"
        arnold_sub_data[trace_sets] = cmds.getAttr(trace_sets)
        # subdivision
        aiSubdivType = mesh + ".aiSubdivType"
        arnold_sub_data[aiSubdivType] = cmds.getAttr(aiSubdivType)

        aiSubdivIterations = mesh + ".aiSubdivIterations"
        arnold_sub_data[aiSubdivIterations] = cmds.getAttr(aiSubdivIterations)

        aiSubdivAdaptiveMetric = mesh + ".aiSubdivAdaptiveMetric"
        arnold_sub_data[aiSubdivAdaptiveMetric] = cmds.getAttr(aiSubdivAdaptiveMetric)

        aiSubdivPixelError = mesh + ".aiSubdivPixelError"
        arnold_sub_data[aiSubdivPixelError] = cmds.getAttr(aiSubdivPixelError)

        aiSubdivAdaptiveSpace = mesh + ".aiSubdivAdaptiveSpace"
        arnold_sub_data[aiSubdivAdaptiveSpace] = cmds.getAttr(aiSubdivAdaptiveSpace)

        aiSubdivUvSmoothing = mesh + ".aiSubdivUvSmoothing"
        arnold_sub_data[aiSubdivUvSmoothing] = cmds.getAttr(aiSubdivUvSmoothing)

        aiSubdivSmoothDerivs = mesh + ".aiSubdivSmoothDerivs"
        arnold_sub_data[aiSubdivSmoothDerivs] = cmds.getAttr(aiSubdivSmoothDerivs)

        aiSubdivFrustumIgnore = mesh + ".aiSubdivFrustumIgnore"
        arnold_sub_data[aiSubdivFrustumIgnore] = cmds.getAttr(aiSubdivFrustumIgnore)

        # displacement Attributes
        aiDispHeight = mesh + ".aiDispHeight"
        arnold_sub_data[aiDispHeight] = cmds.getAttr(aiDispHeight)

        aiDispPadding = mesh + ".aiDispPadding"
        arnold_sub_data[aiDispPadding] = cmds.getAttr(aiDispPadding)

        aiDispZeroValue = mesh + ".aiDispZeroValue"
        arnold_sub_data[aiDispZeroValue] = cmds.getAttr(aiDispZeroValue)

        cmds.select(mesh)
        select_mesh = cmds.ls(sl=True, long=True)[0]

        getDisplaySmoothness = cmds.displaySmoothness(q=True, polygonObject=True)
        arnold_sub_data["getDisplaySmoothness"] = getDisplaySmoothness

        # if "|master|poly" in select_mesh:
        #     mesh_info[select_mesh] = arnold_sub_data

        mesh_info[select_mesh] = arnold_sub_data

    return mesh_info


def get_all_mesh():
    '''得到shader对应的mesh

    Returns:
        {u'phoenix_NM':[
            u'|master|shape|jiaobei_r_shape.f[0:8250]',
            u'|master|shape|jiaobei_l_shape.f[0:8250]'
            ],
        ...

    '''

    shading_group = cmds.ls(type="shadingEngine")
    mesh_shader_dict = {}
    for node in shading_group:
        shader_list = cmds.listConnections("{0}.surfaceShader".format(node))
        if not shader_list:
            continue
        for shader in shader_list:
            cmds.select(shader)
            # 列出材质赋予的所有面
            cmds.hyperShade(objects="")
            select_mesh = cmds.ls(sl=True, long=True)

            # select_mesh_final = []
            # check_path_result = False
            # for i in select_mesh:
            #     if "|master|poly" in i:
            #         check_path_result = True
            #         select_mesh_final.append(i)
            #     if select_mesh_final and check_path_result:
            #         mesh_shader_dict[shader] = select_mesh_final
            #         cmds.select(cl=True)

            # 应下游（ani， cfx）对颜色的需求，现在改为所有的shader 都导出去
            mesh_shader_dict[shader] = select_mesh
            cmds.select(cl=True)
    return mesh_shader_dict


def output_json_file(shader_mesh_data, mesh_arnold_info, maya_shader_path):
    # export json file
    shader_output_json = os.path.join(maya_shader_path, "shader_output.json")
    arnold_data_json = os.path.join(maya_shader_path, "arnold_data.json")
    with open(shader_output_json, "w") as shader_output_json_file:
        json.dump(shader_mesh_data, shader_output_json_file, ensure_ascii=False, indent=4)
    with open(arnold_data_json, "w") as arnold_data_json_file:
        json.dump(mesh_arnold_info, arnold_data_json_file, ensure_ascii=False, indent=4)
    # export shader
    for shader_b in shader_mesh_data.keys():
        cmds.select(shader_b)
        shader_path = os.path.join(maya_shader_path, shader_b + ".mb")
        if os.path.exists(shader_path):
            os.remove(shader_path)
        print shader_path
        cmds.file(shader_path, op="v=0;", typ="mayaBinary", pr=True, es=True, f=True)


def get_data(path):
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    katana_shader_path = path
    mesh_shader_dict = get_all_mesh()
    mesh_info = get_arnold_data()
    output_json_file(mesh_shader_dict, mesh_info, katana_shader_path)
    print mesh_shader_dict
    print mesh_info


def fix_eyeball_geo_transparency(shape, value=1):


    # 获取 ShadingEngine
    sgs = cmds.listConnections(shape, type="shadingEngine") or []
    if not sgs:
        return

    # 获取材质
    materials = cmds.ls(
        cmds.listConnections(sgs[0] + ".surfaceShader"),
        materials=True
    )

    if not materials:
        return

    mat = materials[0]

    # 设置 Transparency
    if cmds.attributeQuery("transparency", node=mat, exists=True):
        cmds.setAttr(mat + ".transparency", value, value, value, type="double3")
    return


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出maya材质球信息为json、mb 。"
        self.description = u"输出maya材质球信息为json、mb"
        return

    def connect_lc_switch(self, asset_name=None):
        all_input = []
        switch_nodes = []
        for layer_tex_node in cmds.ls(typ='layeredTexture'):

            connection_nodes  = cmds.listConnections(layer_tex_node + '.inputs')
            if not connection_nodes:
                continue
            for connection_node in list(set(connection_nodes)):
                if cmds.objectType(connection_node) == 'lc_switch':
                    cmds.delete(connection_node)


            for attr in cmds.listAttr(layer_tex_node, multi=True, connectable=True):
                if attr.startswith('inputs') and attr.split('.')[0] not in all_input:
                    all_input.append(attr.split('.')[0])

            if not cmds.pluginInfo('switchNode', loaded=True, q=True):
                cmds.loadPlugin('switchNode')

            lc_switch_node = cmds.shadingNode('lc_switch', asUtility=True, n=layer_tex_node + '_switch')
            switch_nodes.append(asset_name + "_" + lc_switch_node)
            lc_switch_attr = sorted([lc_attr for lc_attr in  cmds.listAttr(lc_switch_node) if lc_attr.startswith('outAlpha_')])
            for i, layer_attr in enumerate(all_input):
                cmds.connectAttr(lc_switch_node + '.' + lc_switch_attr[i], layer_tex_node + '.' + layer_attr + 'isVisible')
                cmds.connectAttr(lc_switch_node + '.' + lc_switch_attr[i], layer_tex_node + '.' + layer_attr + 'alpha')

        return switch_nodes

    @record_time(__file__)
    def proceed(self):
        try:
            self.dialog.switch_nodes = []
            mesh_array = cmds.listRelatives('|master|poly|hi|mesh_grp',type="mesh", ad=True, f=True)
            for mesh in mesh_array:
                if cmds.attributeQuery('lc_transparent', node=mesh, exists=True):
                    cmds.setAttr(mesh+'.lc_transparent',l=False)
                    cmds.deleteAttr(mesh+'.lc_transparent')
                    if mesh.endswith('_eyeball_geoShape'):
                        fix_eyeball_geo_transparency(mesh)

            mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
            for asset_name in self.dialog.d_assets_info.keys():
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                maya_shader_path = os.path.join(version_dir,'maya_shaders')
                maya_tex_path = os.path.join(version_dir, 'images', 'tex_low')
                if not os.path.exists(maya_shader_path):
                    os.makedirs(maya_shader_path, 0o777)

                if not os.path.exists(maya_tex_path):
                    os.makedirs(maya_tex_path, 0o777)

                for file_node in pm.ls(typ='file'):
                    tex_path = pm.getAttr(file_node + '.fileTextureName')
                    if not tex_path or tex_path.startswith('Z') or tex_path.startswith('/ment/proj') or '/srf/' in tex_path.replace('\\', '/') or 'tex_low' in tex_path.replace('\\', '/'):
                        continue
                    new_tex = os.path.join(maya_tex_path, os.path.basename(tex_path))
                    pm.setAttr(file_node + '.fileTextureName', new_tex)

                self.dialog.switch_nodes = self.connect_lc_switch(asset_name)
                mesh_shader_dict = get_all_mesh()

                mesh_info = get_arnold_data()
                output_json_file(mesh_shader_dict, mesh_info, maya_shader_path)
                return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
