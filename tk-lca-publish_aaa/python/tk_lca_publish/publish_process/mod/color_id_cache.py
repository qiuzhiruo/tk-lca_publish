# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yu Huazhuo
#
# Date: 2017.03
#
# Description:
#
############################################

import os
import traceback
import shutil
import math
import pymel.core as pm

import proc.set_asset_color_id as sci
from proc.function_running_time import record_time

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出Color id Cache。"
        self.description = u"输出Color id Cache。"
        return

    def create_n_assign_shader(self, l_meshes, shader_name, color, transparency):
        new_color = [float(c)/255.0 for c in color]
        shader = pm.shadingNode('lambert', asShader=True, name=shader_name)
        shader_sg = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=shader_name+'SG')
        pm.connectAttr(shader.name()+'.outColor', shader_sg.name()+'.surfaceShader', f=True)

        shader.setAttr('transparency', transparency)
        shader.setAttr('color', new_color)
        l_meshes = [mesh.fullPath() for mesh in l_meshes]

        print 'v' * 500
        for o_mesh in l_meshes:
            pm.select(o_mesh, r=True)
            try:
                pm.sets(shader_sg, e=True, forceElement=True)
            except Exception as e:
                print o_mesh, '<<<<<<<<'
                print shader_sg, '<<<<<<'
                continue

    def get_wire_width(self, trans):
        bb = trans.getBoundingBox()
        max_axial = max(bb[1][0] - bb[0][0], bb[1][1] - bb[0][1], bb[1][2] - bb[0][2])
        edge_cnt = pm.polyEvaluate(trans,  edge=True)
        ww = max_axial/math.sqrt(edge_cnt)/10.0
        return min(10, max(ww, 0.001))

    def out_color_id_cache(self, color_id, cache_path):
        pm.undoInfo( state=True, infinity=True )
        pm.undoInfo(ock=True)
        mod_path = pm.PyNode('|master|poly|hi')
        l_se = pm.ls(type='shadingEngine')

        d_meshes = {'transparency':[], 'opacity':[], 'wireframe':[]}
        for se in l_se:
            #print pm.listConnections(se.name()+'.surfaceShader')
            #print pm.listConnections(se.name()+'.dagSetMembers')
            l_shaders = pm.listConnections(se.name()+'.surfaceShader')
            if len(l_shaders) != 1:
                continue
            shader = l_shaders[0]
            try:
                trans = shader.getAttr('transparency')
            except:
                trans=[0,0,0]

            if trans[0] + trans[1] + trans[2] > 0.3:
                key = 'transparency'
            else:
                key = 'opacity'

            for transform in pm.listConnections(se.name()+'.dagSetMembers'):
                if transform.nodeType() != 'transform':
                    continue
                if mod_path.isParentOf(transform):
                    d_meshes[key].append(transform)

        wf_group = pm.createNode('transform', name='wireframe_group', parent=mod_path)
        for trans in d_meshes['transparency']:
            for mesh in pm.listRelatives(trans, children=True, type='mesh', noIntermediate=True):
                mesh_name = mesh.name()
                wf_node = pm.createNode( 'lcaWireframeNode', name=mesh_name+'_wf_node' )
                wf_trans = pm.createNode( 'transform', name=mesh_name+'_wf', parent=wf_group )
                wf_mesh = pm.createNode( 'mesh', name=mesh_name+'_wfShape', parent=wf_trans )
                pm.connectAttr( mesh_name + '.outMesh', wf_node.name()+'.inputMesh' )
                pm.connectAttr( wf_node.name() + '.outputMesh', wf_mesh.name()+'.inMesh' )
                pm.setAttr(wf_node.name() + ".wireWidth", self.get_wire_width(trans))
                d_meshes['wireframe'].append(wf_trans)

        pm.hide(d_meshes['transparency'])
        self.create_n_assign_shader(d_meshes['opacity'], 'opacity_s', color_id, (0, 0, 0))
        self.create_n_assign_shader(d_meshes['wireframe'], 'wireframe', color_id, (0, 0, 0))

        pm.undoInfo(cck=True)
        pm.loadPlugin('gpuCache', quiet=True)

        pm.gpuCache(mod_path, startTime=1, endTime=1, optimize=True, optimizationThreshold=40000, writeMaterials=True, directory=cache_path, fileName='color_id')
        pm.undo()
        pm.undoInfo( state=True, infinity=False )

        f = open(os.path.join(cache_path,"transparent_meshes.txt"), 'w')
        for n in d_meshes['transparency']:
            f.write(n.name()+'\n')
        f.close()

    @record_time(__file__)
    def proceed(self):
        try:
            pm.loadPlugin('gpuCache', quiet=True)
            pm.loadPlugin('wireframe.py', quiet=True )
            # Smooth display mesh with subd in name
            l_meshes = pm.ls( type='mesh')
            for mesh in l_meshes:
                if '_SUBD|' in mesh.fullPath():
                    pm.displaySmoothness(mesh, polygonObject=3)

            for asset_name in self.dialog.d_assets_info.keys():
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                root = self.dialog.d_assets_info[asset_name]['node']
                node_name = self.dialog.d_assets_info[asset_name]['node_name']
                parent = self.dialog.d_assets_info[asset_name]['parent']
                translation = self.dialog.d_assets_info[asset_name]['translation']
                rotation = self.dialog.d_assets_info[asset_name]['rotation']
                asset_type = self.dialog.d_assets_info[asset_name]['type']

                asset_color_id_str = sci.get_color_id(self.dialog.project['name'], asset_name, self.dialog.sg)
                asset_color_id = asset_color_id_str.split(' ')
                # make a master if necessary
                if parent:
                    pm.parent(root, world=True)

                if node_name != 'master':
                    root.rename('master')

                root.setRotation((0.0, 0.0, 0.0))
                pm.xform(root, r=True, translation=(translation[0] * -1,  translation[1] * -1, translation[2] * -1))

                # Create dirs
                if not os.path.isdir(version_dir + '/gpu'):
                    os.makedirs(version_dir + '/gpu')

                for res in ['|master|poly|hi']:
                    if len(pm.listRelatives(res, ad=True, type='mesh')) == 0:
                        continue
                    try:
                        proxy=pm.listRelatives(res, ad=True)
                        for p in proxy:
                            pm.setAttr(p+'.visibility', 1)
                    except:
                        print 'Faild to set vis for', res

                    version_gpu=version_dir + '/gpu'

                    self.out_color_id_cache(color_id=asset_color_id, cache_path=version_gpu)
                # recovery root node
                root.setRotation(rotation)
                if parent:
                    pm.parent(root, parent)

                root.rename(node_name)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


