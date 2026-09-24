# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yingjie
#
#
# Description: 
#
############################################

import os
import traceback
import shutil
from sgtk.platform.qt import QtGui

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"添加shotgun最新的lookPass和拉材质"
        self.description = u"从shotgun上读取最新的lookPass和拉材质"
        return

    def apply_srf_shader(self):
        # asset = self.dialog.entity['name']
        # proj = self.dialog.project['name']
        # import srf.push_shader.push_shader as sps
        # sps.push_shader(proj,asset,force=True,add_pass_only=True)
        # self.dialog.print_log(u'添加pass list到'+proj+':'+asset)

        import srf.push_shader.push_rig_shader as sp
        reload(sp)
        sp.push_rig_shader()
        return ""

    def proceed(self):
        try:
            self.apply_srf_shader()
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description








