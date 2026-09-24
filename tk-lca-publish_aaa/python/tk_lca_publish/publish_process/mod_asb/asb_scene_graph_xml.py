# -*- coding:utf-8 -*-

import os
import traceback
import math
import shutil
import pymel.core as pm

import sys
sys.path.append( '/'.join(os.path.dirname(__file__).replace('\\','/').split('/')[:-1]) + '/gen' )
import sgXml_parser as sgxml


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出Assembly Scene Graph Xml 文件。"
        self.description = u"Assembly Scene Graph Xml文件可以用来将asb文件组合拼装成资产和场景。"
        return

    def proceed(self):
        try:
            self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'

            root = pm.PyNode('|master')

            # Add version mark
            l_attrs = pm.listAttr(root)
            if not 'asbVersion' in l_attrs:
                pm.addAttr(root, shortName='asbv', longName='asbVersion', dt="string")
            if not 'asbPath' in l_attrs:
                pm.addAttr(root, shortName='asbp', longName='asbPath', dt="string")

            pm.setAttr( "|master.asbVersion", self.dialog.version_name[-3:], type="string" )
            pm.setAttr( "|master.asbPath", self.dialog.tank_file, type="string" )

            # export scene graph xml
            if os.path.isdir(self.dialog.version_dir + '/scene_graph_xml'):
                shutil.rmtree(self.dialog.version_dir + '/scene_graph_xml')

            os.makedirs(self.dialog.version_dir + '/scene_graph_xml')
            asb_xml_path = self.dialog.version_dir + '/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
            # export asb xml file
            xml = sgxml.SgXmlParser()
            xml.exportXml(root, asb_xml_path)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


