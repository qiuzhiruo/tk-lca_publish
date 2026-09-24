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
from third_party.sceneGraphXML import maya2scenegraphXML
import pymel.core as pm
from xml.etree import ElementTree

import production.pipeline.ShotGunProj as csgp


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出Scene Graph Xml 文件。"
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
                self.delete_ai(tank_file)

                pm.openFile(tank_file, f=True)

                pm.mel.eval('python(\"import third_party.sceneGraphXML.maya2scenegraphXML as maya2scenegraphXML\");')
                master_node = pm.ls('master')[0]
                xmlFilePath = version_dir + '/scene_graph_xml/' + asset_name + '.xml'
                # xmlFilePath = '/mnt/work/shome/houaokang/test/mod/agx.xml'
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
                maya2scenegraphXML.deleteSgxmlAttrs('|master')
                pm.newFile(f=True)

            if os.path.isfile(version_up):
                pm.openFile(version_up, f=True)
            else:
                pm.openFile(ma_file, f=True)

            return ''

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


