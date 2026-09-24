# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Jingwei Wan
#
# Date: 2018.11
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
        self.process_name = u"复制文件到crd_oat任务"
        self.description = u"复制文件到crd_oat任务作为v000版"
        return


    def proceed(self):
        try:
            import pymel.core as pm
            # Copy ma file
            ma_file = self.dialog.version_dir + '/' + os.path.basename(pm.sceneName()).split(".")[0] + ".ma"
            print ma_file
            if os.path.isfile(ma_file):
                work_root = self.dialog.ctx.filesystem_locations[0]
                print 'work_root', work_root            
                
                shot = self.dialog.ctx.entity['name']
                oat_ma = shot + '.crd.crd_oat.v000.ma'
                oat_work_dir = os.path.join(work_root, 'crd/task/maya')
                oat_work_file = os.path.join(oat_work_dir, oat_ma)
                if not os.path.isdir(os.path.join(work_root, 'crd/task/maya')):
                    os.makedirs(oat_work_dir, 0777)
                print 'oat_work_file', oat_work_file
                shutil.copyfile(ma_file, oat_work_file)
                os.chmod(oat_work_file,0777)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

