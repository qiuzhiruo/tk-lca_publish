# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2017.08
#
# Description: inherit from sg_asset_links, to create a version description for how many
#              assets the shot have, and how heavy the shot it
#
########################################################################################

import os
import traceback
import pymel.core as pm
import proc.xml_scene_summary as xml_scene_summary


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog       
        self.process_name = u"描述镜头内资产数和资产面数"
        self.description = u"描述镜头内资产数和资产面数"
        return


    def proceed(self):
        try:

            if not pm.objExists('|assets'):
                return ""

            self.scene_xml_path = self.dialog.version_dir + '/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
            if os.path.isfile(self.scene_xml_path):
                self.scene_description()

            return ""

        except:
            return traceback.format_exc()


    def scene_description(self):
        txt = self.dialog.w_publish.plainTextEdit_auto_description.toPlainText()
        if txt != '':
            txt += '\n'

        txt += xml_scene_summary.summarize(self.scene_xml_path, self.dialog.sg, self.dialog.project, {})
        self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(txt)

        return


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


