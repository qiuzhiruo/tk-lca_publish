# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2017.04
#
# Description: Copy model xml / cache files to the rig version
#
############################################

import os
import traceback
import shutil
import pymel.core as pm

try:
    scene_graph_xml_path = os.path.dirname(__file__).replace('\\','/')+'/scene_graph_xml'
except:
    scene_graph_xml_path = r"D:\program\tk-lca-publish\python\tk_lca_publish\publish_process\rig\scene_graph_xml"

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝模型版本的 xml 和 gpu cache 文件"
        self.description = u"拷贝模型版本的 xml 和 gpu cache 文件。"
        return


    def proceed(self):
        try:
            for src_dir_name in ['scene_graph_xml', 'gpu']:
                src_path = ''
                if pm.objExists('|master'):
                    m = pm.PyNode('|master')
                    if m.hasAttr('modPath'):
                        src_dir = os.path.dirname(pm.getAttr('|master.modPath').replace('\\', '/')) + '/' + src_dir_name 
                        if os.path.isdir(src_dir):
                            src_path = src_dir

                src_dir_path = self.dialog.version_dir + '/' + src_dir_name

                if src_path == '':
                    rig_publish_dir = os.path.dirname(self.dialog.version_dir)
                    mod_publish_dir = rig_publish_dir.replace('/rig/', '/mod/')
                    src_dir = mod_publish_dir + '/' + self.dialog.entity['name'] + '.mod.model/' + src_dir_name
                    if os.path.isdir(src_dir):
                        src_path = src_dir

                if src_path != '':

                    try:
                        if os.path.isdir(src_dir_path):
                            shutil.rmtree(src_dir_path)
                    except:
                        pass

                    shutil.copytree(src_path, src_dir_path)

                    if src_dir_name == 'scene_graph_xml':
                        if not os.path.isfile(src_dir_path+"/%s.xml"%self.dialog.entity['name']):
                            xml = [a for a in os.listdir(src_dir_path) if ".xml" in a][0]
                            os.rename(src_dir_path+"/"+xml, src_dir_path+"/%s.xml"%self.dialog.entity['name'])

                elif src_path == '' and src_dir_name == 'scene_graph_xml':
                    try:
                        if os.path.isdir(src_dir_path):
                            shutil.rmtree(src_dir_path)
                    except:
                        pass
                    shutil.copytree(scene_graph_xml_path, src_dir_path)
                    os.rename(src_dir_path+"/orig.xml", src_dir_path+"/%s.xml"%self.dialog.entity['name'])

            return ""


        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

