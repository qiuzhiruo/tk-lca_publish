# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.05
#
# Description:
#
############################################

import os
import sys
import traceback
import shutil
import pymel.core as pm
import re
from proc.function_running_time import record_time

# All publish process will use StdProcess as the class name.
def getcolor(image_path):
    from  PIL import Image,ImageStat
    if image_path.endswith('tif') or image_path.endswith('tx'):
        return [0.5,0.5,0.5]

    img=Image.open(image_path)
    color_list=ImageStat.Stat(img).mean
    cv=[c/255.0*1.2 for c in color_list]
    mc=max(cv)
    for i,c in enumerate(cv):
        if mc==c:
            cv[i]=mc*1.2
    return cv


def tex2color():
    file_list=pm.ls(type='file')
    shader_list={}
    for tex in file_list:
        tex_path=pm.getAttr(tex+'.fileTextureName')
        if not os.path.isfile(tex_path):
            continue

        color=getcolor(tex_path)
        l_shader=pm.listConnections(tex,type='lambert')

        for shader in l_shader:
            if pm.nodeType(shader) != 'lambert':
                continue
            if shader.attr('color').inputs():
                pm.disconnectAttr(tex+'.outColor',shader+'.color')
                pm.setAttr(shader+'.color',color)
                shader_list[tex+'.outColor']=shader+'.color'

    return shader_list

class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出GPU Cache和Assembly 。"
        self.description = u"输出GPU Cache和Assembly。"
        return

    @record_time(__file__)
    def proceed(self):

        try:
            shader_list=tex2color()

            publish_dir = self.dialog.publish_root
            if '/rig/' not in publish_dir:
                pm.loadPlugin('gpuCache', quiet=True)
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
                publish_dir = self.dialog.publish_root
                version_name = self.dialog.version_name
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
                if not os.path.isdir(version_dir + '/assembly_definition'):
                    os.makedirs(version_dir + '/assembly_definition')

                for res in ['|master|poly|hi', '|master|poly|proxy']:
                    if pm.objExists(res):
                        if len(pm.listRelatives(res, ad=True, type='mesh')) == 0:
                            continue
                        try:
                            proxy=pm.listRelatives(res, ad=True)
                            for p in proxy:
                                try:
                                    pm.setAttr(p+'.visibility', 1)
                                except:
                                    pass
                        except:
                            print 'Faild to set vis for', res
                        res_and_shape=[res]
                        if pm.objExists('|master|shape') and asset_type == 'env':
                            res_and_shape.append('|master|shape')
                        if pm.objExists('|master|shape|efx_grp') and asset_type == 'prp':
                            res_and_shape.append('|master|shape|efx_grp')
                        if '/rig/' not in publish_dir:
                            pm.gpuCache(res_and_shape, startTime=1, endTime=1, optimize=True, optimizationThreshold=40000, writeMaterials=True, saveMultipleFiles=False, directory=version_dir + '/gpu', dataFormat='ogawa', fileName= res.split('|')[-1])
                        else:
                            mode_gpu_path = publish_dir.replace('/rig/','/mod/') + '/' + asset_name + '.mod.model/gpu'
                            rig_gpu_path = version_dir + '/gpu'
                            if os.path.isdir(mode_gpu_path):
                                if os.path.exists(rig_gpu_path):
                                    shutil.rmtree(rig_gpu_path)
                                shutil.copytree(mode_gpu_path, rig_gpu_path)
                #build gpu ma
                res_list=[]
                for res in ['md','lo','proxy']:
                    res_path='|master|poly|'+res
                    if pm.objExists(res_path):
                        res_list.append(pm.PyNode(res_path))
                        pm.parent(res_path,world=True)

                if pm.objExists('|master|rig'):
                    pm.parent('|master|rig',world=True)

                if '/rig/' not in publish_dir:
                    pm.gpuCache('|master', startTime=1, endTime=1, optimize=False, writeMaterials=True, saveMultipleFiles=False, directory=version_dir + '/gpu_ma', dataFormat='ogawa', fileName= asset_name)
                else:
                    mode_ma_gpu_path = publish_dir.replace('/rig/', '/mod/') + '/' + asset_name + '.mod.model/gpu_ma'
                    rig_ma_gpu_path = version_dir + '/gpu_ma'
                    if os.path.isdir(mode_ma_gpu_path):
                        if os.path.exists(rig_ma_gpu_path):
                            shutil.rmtree(rig_ma_gpu_path)
                        shutil.copytree(mode_ma_gpu_path, rig_ma_gpu_path)
                for res in res_list:
                    if pm.objExists(res):
                        pm.parent(res,'|master|poly|')

                if pm.objExists('rig'):
                    pm.parent('rig','|master')

                gpu_hi = version_dir + '/gpu/hi.abc'
                gpu_proxy = version_dir + '/gpu/proxy.abc'
                gpu_color_id = version_dir + '/gpu/color_id.abc'

                maya_proxy = version_dir + '/res/proxy/' + asset_name + '.mb'
                assembly_file = version_dir + '/assembly_definition/' + asset_name + '.ma'
                # maya_hi = version_dir + '/res/hi/' + asset_name + '.ma'
                if self.dialog.task['name'] in ['model','assembly']:
                    maya_hi = version_dir + '/res/hi/' + asset_name + '.mb'
                else:
                    maya_hi = version_dir + '/' + asset_name + '.mb'
                    
                    
                gpu_all = version_dir + '/gpu_ma/'+asset_name+'.abc'
                gpu_ma = version_dir + '/gpu_ma/'+asset_name+'.ma'

                #
                rig_publish_dir = publish_dir.replace('mod', 'rig')
                rig_version_name = re.split('\.v\d+$', version_name)[0].replace('mod.model', 'rig.rigging_layout')
                rig_lay_file_path = rig_publish_dir + '/' +rig_version_name + '/' +'{}.ma'.format(asset_name)
                #
                if sys.platform.startswith('win'):
                    version = pm.about(v=True)
                    maya_py = r'"C:/Program Files/Autodesk/Maya{version}/bin/mayapy.exe"'.format(version=version)
                else:
                    maya_py = '{}/launchers/nyj/linux/mayapy'.format(os.getenv('LCA_REZ'))

                # build_py = os.path.join(os.path.dirname(__file__),'build_gpu_ma.py')
                # cmd_str=maya_py+' '+build_py+' '+gpu_all
                # print cmd_str
                # import subprocess
                # p = subprocess.Popen(cmd_str, shell=True, stdin= subprocess.PIPE, stdout= subprocess.PIPE,stderr=subprocess.STDOUT)
                # out, err=p.communicate()
                # print out
                # print err

                if not os.path.isfile(gpu_proxy):
                    gpu_proxy = gpu_hi

                if asset_type == 'flg':
                    gpu_cache = gpu_proxy
                else:
                    gpu_cache = gpu_hi

                shutil.copyfile(os.path.dirname(__file__)+'/assembly_definition.ma', assembly_file)
                f = open(assembly_file, 'r')
                l_lines = f.readlines()
                f.close()
                f = open(assembly_file, 'w')
                for line in l_lines:
                    new_line = line.replace('{ASSET}', asset_name)
                    new_line = new_line.replace('{GPU_CACHE}', gpu_cache)
                    new_line = new_line.replace('{MAYA_FILE}', gpu_ma)
                    new_line = new_line.replace('{GPU_CACHE_HI}', gpu_hi)
                    new_line = new_line.replace('{MAYA_FILE_HI}', gpu_ma)
                    if 'rep[0].rda' in line and asset_type=='env':
                        new_line = new_line.replace('{GPU_CACHE_PROXY}', gpu_hi)
                    else:
                        new_line = new_line.replace('{GPU_CACHE_PROXY}', gpu_proxy)
                    new_line = new_line.replace('{GPU_CACHE_COLOR_ID}', gpu_color_id)
                    new_line = new_line.replace('{MAYA_FILE_PROXY}', maya_proxy)
                    new_line = new_line.replace('{MAYA_FILE_hi}', maya_hi)
                    new_line = new_line.replace('{MAYA_FILE_Lay_rig}', rig_lay_file_path)
                    f.write(new_line)
                f.close()

                self.dialog.assembly_definition = assembly_file

                # recovery root node
                pm.xform(root, r=True, translation=(translation[0],  translation[1], translation[2]))
                root.setRotation(rotation)
                if parent:
                    pm.parent(root, parent)

                if node_name != 'master':
                    root.rename(node_name)

                self.dialog.d_assets_info[asset_name]['assembly_file'] = assembly_file

            for mesh in l_meshes:
                pm.displaySmoothness(mesh, polygonObject=0)

            for key in shader_list.keys():
                pm.connectAttr(key,shader_list[key])
            return ""

        except:

            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


