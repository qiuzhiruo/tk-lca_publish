# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.12
#
# Description: Create a sene graph xml file for the asset
#
############################################

import os
import sys
import shutil
import traceback
import re

# sys.path.append('U:/toolset/lib/3rd_party/sceneGraphXML')
# sys.path.append('/mnt/utility/toolset/lib/3rd_party/sceneGraphXML')
# sys.path.append('/Volumes/utility/toolset/lib/3rd_party/sceneGraphXML')

# from third_party.sceneGraphXML import maya2scenegraphXML
#  use 3rd_party
sys.path.append(os.getenv('LC_UTILITY').replace('\\','/') + '/toolset/lib/3rd_party/sceneGraphXML')
import maya2scenegraphXML

import pymel.core as pm
from xml.etree import ElementTree

import production.pipeline.ShotGunProj as csgp


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出Scene Graph Xml 文件。"
        self.description = u"Scene Graph Xml文件可以用来将将abc文件组合拼装成资产和场景。"
        return

    def replaceBBoxWithLo(self, scene_xml_path):
        '''
        modify xml, need input the path to xml file
        '''
        # Reset bounds and xform
        if pm.objExists('|master|poly|lo'):
            bb = pm.PyNode('|master|poly|lo').getBoundingBox(invisible=True, space='world')
        else:
            return

        tree = ElementTree.parse(scene_xml_path)
        root = tree.getroot()

        l_instances = root.getiterator("instance")
        for i in l_instances:
            if i.attrib['name'] in ['master', 'poly', 'hi']:
                i.getiterator('bounds')[0].attrib = {'minx':str(bb.min()[0]), 'miny':str(bb.min()[1]), 'minz':str(bb.min()[2]), 'maxx':str(bb.max()[0]), 'maxy':str(bb.max()[1]), 'maxz':str(bb.max()[2])}
        tree.write(scene_xml_path)

    def convert_file(self, src, dst):
        cmd = '"' + self.dialog.rvio_path + '" ' + src + ' -o ' + dst
        ext_src = src.lower().split('.')[-1]
        current_proj = self.dialog.project['name']
        shotgunProj = csgp.ShotGunProj(current_proj)
        color_space_proj = shotgunProj.get_color_space_info()
        if color_space_proj['sg_color_space'] == "ACES" and ext_src.endswith('.exr'):
            rv_template_path = '/mnt/work/software/color_management/OpenColorIO-Configs/rv_template/aces_1.2/exr2movjpg_single.rv'
            ocio_path = os.path.join('/mnt/work/software/color_management/OpenColorIO-Configs','aces_1.2','config.ocio')
            cmd = "ocio_path={ocio_path} RV_PATHSWAP_SOURCE_A='{input_path}' {rvio}  {rv_template} -o {output_path}".format(
                ocio_path = ocio_path,
                input_path = src,
                rvio=self.dialog.rvio_path,
                rv_template=rv_template_path,
                output_path=dst
		    )
        elif ext_src == 'exr':
            cmd += ' -outsrgb'

        os.system(cmd)
        return

    def delete_ai(self, file):
        ai_transform_re = re.compile(r'.*\"\.ai_translator"\s\-type\s\"string\".*')
        new_line = []
        with open(file, 'r') as f:
            for line in f:
                if ai_transform_re.match(line):
                    continue
                new_line.append(line)

        nf = open(file, 'w+')
        for line in new_line:
            nf.write(line)

        nf.close()
        os.chmod(file, 0774)
        return

    def proceed(self):
        try:
            ma_file = pm.sceneName()
            self.delete_ai(ma_file)
            version_up = ma_file[:-7] + 'v' + format( int(self.dialog.version_num)+1, '#03' ) + '.ma'

            pm.loadPlugin('gpuCache', quiet=True)
            # pm.mel.eval('python(\"import sys;sys.path.append(\\\"U:/toolset/lib/3rd_party/sceneGraphXML\\\");sys.path.append(\\\"/mnt/utility/toolset/lib/3rd_party/sceneGraphXML\\\");sys.path.append(\\\"/Volumes/utility/toolset/lib/3rd_party/sceneGraphXML\\\");import maya2scenegraphXML");')

            for asset_name in self.dialog.d_assets_info.keys():
                tank_file = self.dialog.d_assets_info[asset_name]['tank_file']
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                root = self.dialog.d_assets_info[asset_name]['node']
                node_name = self.dialog.d_assets_info[asset_name]['node_name']

                self.delete_ai(tank_file)

                pm.openFile(tank_file, f=True)

                # screne grab for the asset
                if not os.path.isdir(version_dir + '/preview'):
                    os.makedirs(version_dir + '/preview')

                pm.viewFit()
                pm.playblast( startTime=1, endTime=1,  format="iff", filename= version_dir + '/preview/thumbnail',
                        forceOverwrite=True, sequenceTime=0, clearCache=False, viewer=False,
                        showOrnaments=True, offScreen=True, fp=4, percent=100,
                        compression="jpg", widthHeight=(800, 800), quality=100)

                if os.path.isfile(version_dir + '/preview/thumbnail.0001.jpg'):
                    os.rename(version_dir + '/preview/thumbnail.0001.jpg', version_dir + '/preview/thumbnail.jpg')
                    self.dialog.d_assets_info[asset_name]['thumbnail'] = version_dir + '/preview/thumbnail.jpg'
                    # copy to /thumbnail/
                    import shutil
                    thumbnail_dir = version_dir + '/thumbnail/'
                    if not os.path.isdir(thumbnail_dir):
                        os.makedirs(thumbnail_dir)
                    dst = thumbnail_dir + os.path.basename(str(self.dialog.d_assets_info[asset_name]['thumbnail'])) + '.png'
                    self.convert_file(str(self.dialog.d_assets_info[asset_name]['thumbnail']), dst)

                # Creat XML dir
                if os.path.isdir(version_dir + '/scene_graph_xml'):
                    shutil.rmtree(version_dir + '/scene_graph_xml')

                os.makedirs(version_dir + '/scene_graph_xml')
                xmlFilePath = version_dir + '/scene_graph_xml/' + asset_name + '.xml'
                proxy_path = version_dir + '/scene_graph_xml/proxy.abc'
                misc_path = version_dir + '/scene_graph_xml/misc.abc'
                master_node = pm.PyNode('|master')
               
                l_trans = pm.listRelatives('|master', c=True, fullPath=True)
                for trans in l_trans:
                    if not trans.fullPath() in ['|master|poly']:
                        maya2scenegraphXML.setIgnore([trans.fullPath()])

                l_res = pm.listRelatives("|master|poly", c=True, fullPath=True)
                for res in l_res:
                    if res.fullPath() in ['|master|poly|hi', '|master|poly|md']:
                        maya2scenegraphXML.setComponent([res.fullPath()], refType='abc')
                    else:
                        maya2scenegraphXML.setIgnore([res.fullPath()])

                maya2scenegraphXML.setProxy([ '|master|poly|hi'], 'proxy.abc')

                maya2scenegraphXML.setArbAttr(['|master'], 'modVersion', master_node.attr('modVersion').get(), 'string')

                # Export the scene 
                maya2scenegraphXML.maya2ScenegraphXML(['|master'], xmlFilePath, startFrame=1, endFrame=1, arbAttrs=['modVersion'])

                # Export misc
                if pm.objExists('|master|misc'):
                    pm.AbcExport(j="  -frameRange 1 1 -uvWrite -root |master|misc -file "+misc_path)

                # Cleanup all the attributes that were written on the nodes for the export 
                # (this is optional)
                maya2scenegraphXML.deleteSgxmlAttrs('|master')
                master_node.deleteAttr('arbAttr_modVersion')

                pm.newFile(f=True)

                # Export proxy.abc
                lo_ma = version_dir + '/res_lo/' + asset_name + '.ma'
                if os.path.isfile(lo_ma):
                    pm.openFile(lo_ma, f=True)
                    if pm.objExists('|master|poly|lo'):
                        pm.gpuCache("|master|poly|lo", startTime=1, endTime=1, optimize=True, optimizationThreshold=40000, writeMaterials=False, directory=os.path.dirname(proxy_path), fileName= 'proxy')

                    pm.newFile(f=True)

            if os.path.isfile(version_up):
                pm.openFile(version_up, f=True)
            else:
                pm.openFile(ma_file, f=True)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


