# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Export frame range to shotgun
#
############################################

import os
import traceback
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun设置镜头帧范围。"
        self.description = u"将当前maya文件的Playback的帧范围设置到shotgun相应镜头的 Cut in/Cut out 。"
        return


    def proceed(self):
        try:
            import pymel.core as pm
            cut_in = pm.animation.playbackOptions(q=True, minTime=True)
            cut_out = pm.animation.playbackOptions(q=True, maxTime=True)
            self.dialog.sg.update('Shot', self.dialog.entity['id'], {'sg_cut_in':int(cut_in), 'sg_cut_out':int(cut_out), 'sg_cut_duration':int(cut_out - cut_in +1)})
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


