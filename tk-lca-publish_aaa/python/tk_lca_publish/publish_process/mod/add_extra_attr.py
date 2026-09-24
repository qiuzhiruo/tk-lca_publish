# -*- coding:utf-8 -*-

import sys
import os
import pymel.core as pm
import maya.cmds as cmds
from proc.function_running_time import record_time


class MG:
    attr_list = ['combine_before_cmd', 'combine_after_cmd']


# All publish process will use StdProcess as the class name.
class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"添加额外属性"
        self.description = u"添加额外属性 "
        return

    @record_time(__file__)
    def proceed(self):
        for attr_name in MG.attr_list:
            if not pm.objExists('|master.{}'.format(attr_name)):
                pm.addAttr('|master', longName=attr_name, dataType='string')

        asset = self.dialog.entity['name'].lower()

        proj = self.dialog.project['name'].lower()
        asset_type = self.dialog.d_assets_info[asset]['type']
        if sys.platform.startswith('win'):
            srf_path = 'Z:/projects/{0}/asset/{1}/{2}/srf/publish/{2}.srf.surfacing'.format(proj, asset_type, asset)
        else:
            srf_path = '/mnt/proj/projects/{0}/asset/{1}/{2}/srf/publish/{2}.srf.surfacing'.format(proj, asset_type, asset)

        # 材质村子预览材质则跳过
        if self.dialog.asset_type != 'chr' or os.path.exists(srf_path) and os.path.exists(os.path.join(srf_path, 'tex_low')) and os.path.exists(os.path.join(srf_path, 'mat_info')):
            return ''
        mesh_array = cmds.listRelatives('|master|poly|hi|mesh_grp',type="mesh", ad=True, f=True)
        for mesh in mesh_array:
            if cmds.attributeQuery('lc_transparent', node=mesh, exists=True):
                cmds.setAttr(mesh+'.lc_transparent',l=False)
                cmds.deleteAttr(mesh+'.lc_transparent')

        # 确保没有共用的材质球
        # self.fix_material()
        # 添加属性： lc_transparent （用于控制透明度）
        self.add_transparent_attr()

        return ''

    def fix_material(self):

        skip_shape = ['body_geo', 'mouth_grp', 'L_eyeball_geo_grp', 'R_eyeball_geo_grp']
        for sg in cmds.ls(typ='shadingEngine'):
            materials = cmds.ls(cmds.listConnections(sg + ".surfaceShader"), materials=True)
            connected_shapes = cmds.sets(sg, q=1)
            if not connected_shapes:
                continue
            shape_names = list(set([shape.split('.')[0] for shape in connected_shapes]))
            if not materials or 'lambert1' == materials[0] or not connected_shapes or len(shape_names)<=1:
                continue
            new_mtl_info = {}
            is_remove = False
            for s in shape_names:
                full_path = cmds.ls(s.split('.')[0], long=True)[0]
                if len(set(full_path.split('|')) - set(skip_shape)) != len(full_path.split('|')):
                    shape_names.remove(s)
                    is_remove = True
            if not is_remove:
                shape_names.remove(shape_names[0])

            for shape in shape_names:
                cmds.lockNode('initialShadingGroup', l=False, lockUnpublished=False)
                cmds.lockNode('renderPartition', l=False, lockUnpublished=False)
                new_material = cmds.duplicate(materials[0], un=True, name=materials[0] + '_' + shape.split('.')[0].replace('Shape', ''))[0]
                new_mtl_info.update({shape: new_material})

                new_shading_engine = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=new_material + "SG")
                cmds.connectAttr(new_material + ".outColor", new_shading_engine + ".surfaceShader")
                for obj in [i for i in connected_shapes if i.split('.')[0].startswith(shape)]:
                    cmds.sets(obj, edit=True, forceElement=new_shading_engine)
        pm.mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')

            # for obj in connected_shapes:
            #     full_path = cmds.ls(obj.split('.')[0], long=True)[0]
            #     if len(set(full_path.split('|')) - set(skip_shape)) != len(full_path.split('|')) or obj.split('.')[0] not in new_mtl_info:
            #         continue
            #     obj_name = obj.split('.')[0]
            #     cmds.lockNode('initialShadingGroup', l=False, lockUnpublished=False)
            #     cmds.lockNode('renderPartition', l=False, lockUnpublished=False)
            #     new_shading_engine = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=new_mtl_info[obj_name] + "SG")
            #     cmds.connectAttr(new_mtl_info[obj_name] + ".outColor", new_shading_engine + ".surfaceShader")
            #     cmds.sets(obj, edit=True, forceElement=new_shading_engine)

    def add_transparent_attr(self):
        mesh_array = cmds.listRelatives('|master|poly|hi|mesh_grp',type="mesh", ad=True, f=True)
        for mesh in mesh_array:

            if 'skin_grp' in mesh:
                continue
            shading_engines = cmds.listConnections(mesh, type='shadingEngine')
            lambert_materials = []
            if shading_engines:
                for sg in shading_engines:
                    shaders = cmds.listConnections(sg + '.surfaceShader', source=True, destination=False)
                    for shader in shaders:
                        if shader not in lambert_materials and cmds.attributeQuery('transparency', node=shader, exists=True) and shader!='lambert1':
                            lambert_materials.append(shader)
                if lambert_materials:
                    if cmds.attributeQuery('lc_transparent', node=mesh, exists=True):
                        cmds.setAttr(mesh+'.lc_transparent',l=False)
                        cmds.deleteAttr(mesh+'.lc_transparent')
                    cmds.select(mesh)
                    cmds.addAttr(shortName='lc_transparent', longName='lc_transparent',keyable=False, maxValue=1.0, minValue=0.0)
                    cmds.setAttr(mesh+'.lc_transparent',0.0)
                    cmds.setAttr(mesh+'.lc_transparent',cb=True)
                    for s in lambert_materials:
                        orig_trans = cmds.getAttr(s + '.transparency')[0][0]
                        cmds.setAttr(mesh + '.lc_transparent', orig_trans)
                        try:
                            cmds.connectAttr(mesh+'.lc_transparent',s+'.transparencyR')
                            cmds.connectAttr(mesh+'.lc_transparent',s+'.transparencyG')
                            cmds.connectAttr(mesh+'.lc_transparent',s+'.transparencyB')
                            cmds.setAttr("{}.isHistoricallyInteresting".format(s), 0)
                        except Exception as e:
                            print(e)

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description


