# -*- coding:utf-8 -*-

import os
import traceback
import shutil

import pymel.core as pm
import xml.etree.ElementTree as ET

import sys
# sys.path.append('/mnt/utility/toolset/lib/production/pipeline')
# sys.path.append('U:/toolset/lib/production/pipeline')
import mayaReferenceUtils as mrus
reload(mrus)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将解锁的资产输出到xml文件"
        self.description = u"将解锁的资产输出到xml文件，用于下游识别cache。"
        return

    def proceed(self):
        try:
            asset_selectors = pm.ls('*:asset_selector')
            asset_selectors.extend( pm.ls('*:*:asset_selector') )

            cached = []
            for a in asset_selectors:
                try:
                    if a.hasAttr('activated') and a.attr('activated').get():
                        cached.append( pm.PyNode(a.name().replace(':asset_selector', ':master')) )
                except:
                    print traceback.format_exc()

            if not cached:
                return ""

            xml_path = self.dialog.version_dir + '/cache_xml/'
            xml_name = self.dialog.entity['name'] + '.xml'

            # write to xml
            root = ET.Element('cacheXML')
            root.set('description', 'A list of the assets which should be cached in layout step')

            for c in cached:
                elem = ET.SubElement(root, 'instance')
                elem.set( 'name', c.name().replace(':master', '') )
                ET.SubElement(elem, 'path').set('value', c.fullPath() )

            tree = ET.ElementTree(root)
            if os.path.isdir(xml_path):
                shutil.rmtree(xml_path)
            os.makedirs(xml_path)
            tree.write(xml_path + xml_name)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


