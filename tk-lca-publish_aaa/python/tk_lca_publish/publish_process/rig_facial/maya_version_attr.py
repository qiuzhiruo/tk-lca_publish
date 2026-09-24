# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.08
#
# Description:
#
############################################

import os
import traceback
import shutil
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"文件内标注publish版本。"
        self.description = u"在当前表情文件的facial_root_ctrl控制器上标注publish版本。"
        return


    def proceed(self):
        try:
            if self.dialog.entity['type'] == 'Asset':
                root_node = 'facial_root_ctrl'
                self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'
            else:
                root_node = 'facial_root_ctrl'
                self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.version_name + '.ma'

            dept  = self.dialog.step['name']

            l_attrs = pm.listAttr(root_node)
            if not dept+'Version' in l_attrs:
                pm.addAttr(root_node, shortName = dept+'v', longName = dept+'Version', dt="string")
            if not dept + 'Path' in l_attrs:
                pm.addAttr(root_node, shortName= dept+'p', longName=dept+'Path', dt="string")

            pm.setAttr( root_node + "." + dept + "Version", self.dialog.version_name[-3:], type="string" )
            pm.setAttr(  root_node + "." + dept + "Path", self.dialog.tank_file, type="string" )

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description



