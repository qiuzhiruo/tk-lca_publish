# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.03
#
# Description: 
#
############################################

import os
import traceback
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝 scene graph xml 和 mesh.xml"
        self.description  = u"拷贝 model 任务的 mesh.xml 和调整过的的 scene graph xml。"
        return


    def proceed(self):
        try:
            dst = self.dialog.version_dir + '/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
            shutil.copyfile(self.dialog.dynamic_scene_xml, dst)

            dst = self.dialog.version_dir + '/mesh.xml'
            shutil.copyfile(self.dialog.model_mesh_xml, dst)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


