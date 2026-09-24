# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import os
import traceback
import shutil
import pymel.core as pm


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝stereo.mov到服务器"
        self.description = u"如果stereo.mov存在，拷贝到publish文件夹下，否则忽略"
        return

    def proceed(self):
        try:
            scene_path = str(pm.sceneName()).replace('\\', '/')
            stereo_name = os.path.basename(scene_path)[:-3] + '.stereo.mov'
            preview_3d = os.path.dirname(scene_path) + '/data/' + stereo_name
            if os.path.exists(preview_3d):
                publish_stereo_file = self.dialog.version_dir + '/preview/' + stereo_name
                shutil.copyfile(preview_3d, publish_stereo_file)

            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
