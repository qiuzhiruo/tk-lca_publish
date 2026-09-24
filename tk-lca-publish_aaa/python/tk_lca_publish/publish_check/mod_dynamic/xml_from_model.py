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

import traceback

import os
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查有没有 model 任务的 scene graph xml。"
        self.description = u"Dynamic任务自身缺文件，需要借用 model 任务的 xml"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:

            self.dialog.model_scene_xml = self.dialog.publish_root + '/' + self.dialog.entity['name'] + '.mod.model/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
            if not os.path.isfile(self.dialog.model_scene_xml):
                return u"没有找到模型 XML 文件:" + self.dialog.model_scene_xml

            self.dialog.model_mesh_xml = self.dialog.publish_root + '/' + self.dialog.entity['name'] + '.mod.model/mesh.xml'
            if not os.path.isfile(self.dialog.model_mesh_xml):
                return u"没有找到模型的 Mesh XML 文件:" + self.dialog.model_mesh_xml

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


