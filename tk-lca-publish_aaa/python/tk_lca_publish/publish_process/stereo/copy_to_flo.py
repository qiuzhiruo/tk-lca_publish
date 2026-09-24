# -*- coding:utf-8 -*-

import os
import traceback
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝stereo文件生成flo新的task版本"
        self.description = u"拷贝stereo文件生成flo新的task版本"
        return

    def findLatestVersion(self, filename):
        if not os.path.isfile(filename):
            return filename
        old_version = os.path.basename(filename).split('.')[-2]
        new_version = 'v' + format( int(old_version[1:])+1, '03d' )
        new_filename = os.path.join( os.path.dirname(filename), os.path.basename(filename).replace(old_version, new_version) )
        return self.findLatestVersion(new_filename)

    def proceed(self):
        try:
            import pymel.core as pm
            scene_name = os.path.basename(pm.sceneName())
            path = os.path.dirname(pm.sceneName()).replace('\\', '/')
            if not path.endswith('/'):
                path = path + '/'

            flo_file = self.findLatestVersion( path + scene_name.replace('stereo', 'final_layout') )

            if not os.path.isfile(flo_file):
                shutil.copyfile(pm.sceneName(), flo_file)

            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


