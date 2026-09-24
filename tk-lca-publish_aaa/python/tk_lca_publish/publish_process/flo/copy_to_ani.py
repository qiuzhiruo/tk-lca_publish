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
import ani.lca_vfx_lock.functions as functions_vl
import pymel.core as pm


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"Downstream的flo文件需要准备v000版给ani"
        self.description = u"Downstream的flo文件需要准备v000版给ani"
        return

    def proceed(self):
        try:
            # Copy ma file
            ma_file = self.dialog.version_dir + '/' + os.path.basename(pm.sceneName())
            if os.path.isfile(ma_file):
                folder = self.dialog.version_dir + '/vfx_group'
                functions_vl.record_vfx_info(folder)
                functions_vl.restore_vfx_status_auto()

                work_root = self.dialog.ctx.filesystem_locations[0]
                print 'work_root', work_root  # '/mnt/work/projects/tpr/shot/a60/a60010'

                shot = self.dialog.ctx.entity['name']
                ani_ma = shot + '.ani.animation.v000.ma'
                ani_work_file = os.path.join(work_root, 'ani/task/maya', ani_ma)
                print 'ani_work_file', ani_work_file
                if os.path.exists(ani_work_file):
                    os.remove(ani_work_file)
                shutil.copyfile(ma_file, ani_work_file)
                os.chmod(ani_work_file, 0777)
                functions_vl.restore_vfx_status(folder + '/vfx_status.txt')
                functions_vl.lock_vfx_group()

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
