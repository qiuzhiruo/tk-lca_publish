# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.10
#
# Description: 
#
############################################

# -*- coding:utf-8 -*-

import os
import traceback


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"标记镜头是静/动"
        self.description = u"标记镜头是静/动"
        return

    def proceed(self):
        try:
            mayapy = '"' + os.environ['MAYA_LOCATION'] + '/bin/mayapy"'
            py_script = self.dialog.tool_root + 'toolset/tools/lay/lca_camera_motion/cam_motion.py'
            cmd_str = mayapy + ' ' + py_script + ' ' + self.dialog.project['name'] + ' ' + self.dialog.entity['name']
            os.system(cmd_str)
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
