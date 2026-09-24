# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Copy publish files
#
############################################

import os
import traceback
import shutil


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"保存checked版文件"
        self.description = u"保存checked版文件。"
        return

    def proceed(self):
        try:
            import pymel.core as pm
            import maya.mel as mel

            # force to save the original file and incremental file
            mel.eval('incrementalSaveScene;')

            # Copy ma file
            print 'publish mode:', self.dialog.publish_mode
            if not self.dialog.publish_mode == 1:
                return ""
            
            ma_file = pm.sceneName()
            if os.path.isfile(ma_file):
                folder = os.path.join(os.path.dirname(ma_file), 'checked')
            
            if not os.path.exists(folder):
                os.makedirs(folder)
                os.chmod(folder, 0777)

            checked_file = os.path.join(folder, os.path.basename(ma_file))
            shutil.copyfile(ma_file, checked_file)
            print 'copy checked file: ', checked_file
            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
