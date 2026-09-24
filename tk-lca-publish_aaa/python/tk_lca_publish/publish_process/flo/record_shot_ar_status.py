# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import sys
import os
import copy

import tank
import pymel.core as pm
import pymel.core.nodetypes as nt
import maya.OpenMaya as om

import lay.lca_map_ar.utils.mayaOperations as mayaOps;

reload(mayaOps)
import publish_process.lay_sequence.record_shot_ar_status as rsas;

reload(rsas)
import ani.lca_vfx_lock.functions as functions_vl


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录各个镜头的ar状态"
        self.description = u"记录各个镜头的ar状态到flo publish文件夹, ar_status.txt中, "
        return

    def proceed(self):
        try:
            Rsas = rsas.StdProcess(None)
            ar_dict = Rsas.get_all_ar_status()
            startTime = pm.playbackOptions(query=True, minTime=True)
            pm.currentTime(startTime)
            shot_ar_dict = Rsas.shot_ar_visibility_status(ar_dict)

            ar_info_file = os.path.join(self.dialog.version_dir, 'ar_status.txt')
            with open(ar_info_file, 'w') as op:
                for ar_name in sorted(shot_ar_dict.keys()):
                    op.write(ar_name + '\t' + shot_ar_dict[ar_name] + '\n')

            functions_vl.record_vfx_info(self.dialog.version_dir)

            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
