# -*- coding:utf-8 -*-

import os
import traceback
import math
import shutil
import pymel.core as pm
import json
import maya.cmds as cmds

import sys
sys.path.append( '/'.join(os.path.dirname(__file__).replace('\\','/').split('/')[:-1]) + '/gen' )
import sgXml_parser as sgxml


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出 Scene Graph Xml 文件。"
        self.description = u"Scene Graph Xml文件可以用来将rra文件组合拼装成资产和场景。"
        return

    def proceed(self):
        try:
            self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'

            root = pm.PyNode('|master')

            # Add version mark
            l_attrs = pm.listAttr(root)
            if not 'rraVersion' in l_attrs:
                pm.addAttr(root, shortName='rrav', longName='rraVersion', dt="string")
            if not 'rraPath' in l_attrs:
                pm.addAttr(root, shortName='rrap', longName='rraPath', dt="string")

            pm.setAttr( "|master.rraVersion", self.dialog.version_name[-3:], type="string" )
            pm.setAttr( "|master.rraPath", self.dialog.tank_file, type="string" )

            # export scene graph xml
            if os.path.isdir(self.dialog.version_dir + '/scene_graph_xml'):
                shutil.rmtree(self.dialog.version_dir + '/scene_graph_xml')

            os.makedirs(self.dialog.version_dir + '/scene_graph_xml')
            rra_xml_path = self.dialog.version_dir + '/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
            # export rra xml file
            xml = sgxml.SgXmlParser()
            xml.exportXml(root, rra_xml_path)

            # 写资产中reference文件的模型资产名称
            reference_nodes = [ref for ref in cmds.ls(type="reference") if 'sharedReferenceNode' not in ref] or []
            mode_dit = {}
            mod_list = []
            if reference_nodes:
                for ref in reference_nodes:
                    file_path = cmds.referenceQuery(ref, filename=True)
                    if '.ma' in file_path or '.mb' in file_path:
                        mod_name = file_path.split('/')[-1].split('.')[0]
                        mod_list.append(mod_name)

            mod_list = list(set(mod_list))
            mode_dit['asset_name'] = mod_list

            json_path = self.dialog.version_dir + '/reference_asset.json'
            with open(json_path, 'w') as f:
                json.dump(mode_dit, f, indent=4)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


