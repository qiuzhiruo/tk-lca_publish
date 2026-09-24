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

# sys.path.append('U:/toolset/lib/3rd_party/sceneGraphXML')
# sys.path.append('/mnt/utility/toolset/lib/3rd_party/sceneGraphXML')
# sys.path.append('/Volumes/utility/toolset/lib/3rd_party/sceneGraphXML')
import third_party.sceneGraphXML.maya2scenegraphXML as maya2scenegraphXML
import pymel.core as pm
from xml.etree import ElementTree


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

    def proceed(self):
        try:
            if not pm.objExists('|master|poly|hi'):
                return ""

            pm.loadPlugin('gpuCache', quiet=True)
            pm.mel.eval('python(\"import third_party.sceneGraphXML.maya2scenegraphXML as maya2scenegraphXML\");')

            if os.path.isdir(self.dialog.version_dir + '/scene_graph_xml'):
                shutil.rmtree(self.dialog.version_dir + '/scene_graph_xml')

            os.makedirs(self.dialog.version_dir + '/scene_graph_xml')
            xmlFilePath = self.dialog.version_dir + '/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
            md_path = self.dialog.version_dir + '/scene_graph_xml/md.abc'
            lo_path = self.dialog.version_dir + '/scene_graph_xml/lo.abc'
            proxy_path = self.dialog.version_dir + '/scene_graph_xml/proxy.abc'
            misc_path = self.dialog.version_dir + '/scene_graph_xml/misc.abc'
            shape_path = self.dialog.version_dir + '/scene_graph_xml/shape.abc'
            master_node = pm.PyNode('|master')
           
            l_trans = pm.listRelatives('|master', c=True, fullPath=True)
            for trans in l_trans:
                if not trans.fullPath() in ['|master|poly']:
                    maya2scenegraphXML.setIgnore([trans.fullPath()])

            l_res = pm.listRelatives("|master|poly", c=True, fullPath=True)
            for res in l_res:
                if res.fullPath() in ['|master|poly|hi','|master|poly|md','|master|poly|lo']:
                    maya2scenegraphXML.setComponent([res.fullPath()], refType='abc')
                else:
                    maya2scenegraphXML.setIgnore([res.fullPath()])

            maya2scenegraphXML.setProxy([ '|master|poly|hi'], 'proxy.abc')

            # Export res
            d_res = {'md':md_path, 'lo':lo_path, 'proxy': proxy_path}
            for res in ['md', 'lo', 'proxy']:
                if pm.objExists('|master|poly|'+res) and len(pm.listRelatives('|master|poly|'+res, ad=True, type='mesh')) > 0:
                    try:
                        pm.setAttr('|master|poly|'+res+".visibility", True)
                    except:
                        pass
                    l_trans = [n.name() for n in pm.listRelatives('|master|poly|'+res)]
                    # write colorsets to transfer color to downstream, for VR case and foundation lighting
                    pm.AbcExport(j=" -writeColorSets -frameRange 1 1 -dataFormat ogawa -uvWrite -root " + " -root ".join(l_trans) + " -file " + d_res[res])

                    if res!='proxy':
                        maya2scenegraphXML.setProxy([ '|master|poly|'+res], 'proxy.abc')
                    else:
                        print ' no set proxy ',res

            # Export shape
            if pm.objExists('|master|shape'):
                l_trans = [n.name() for n in pm.listRelatives("|master|shape")]
                pm.setAttr("|master|shape.visibility", True)
                pm.AbcExport(j="  -frameRange 1 1 -dataFormat ogawa -uvWrite -root " + " -root ".join(l_trans) + " -file " + shape_path)

            # Export misc
            if pm.objExists('|master|misc'):
                pm.AbcExport(j="  -frameRange 1 1 -dataFormat ogawa -uvWrite -root |master|misc -file "+misc_path)

            maya2scenegraphXML.setArbAttr(['|master'], 'modVersion', master_node.attr('modVersion').get(), 'string')

            # Export the scene 
            maya2scenegraphXML.maya2ScenegraphXML(['|master'], xmlFilePath, startFrame=1, endFrame=1, arbAttrs=['modVersion'])

            # Cleanup all the attributes that were written on the nodes for the export 
            # (this is optional)
            maya2scenegraphXML.deleteSgxmlAttrs('|master')
            master_node.deleteAttr('arbAttr_modVersion')

            # if there is no object under hi, we need replace the hi's boundingbox with lo
            try:
                hi = pm.PyNode('|master|poly|hi')
                if not hi.listRelatives(c=True, ad=True, type=['mesh', 'nurbsSurface', 'subdiv']):
                    self.replaceBBoxWithLo(xmlFilePath)
            except:
                print 'Failed to rewrite '+xmlFilePath

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description



