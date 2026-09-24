# -*- coding:utf-8 -*-

import os
import traceback
import shutil
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"提取scn资产，将文件拷贝到服务器。"
        self.description = u"将scn文件拷贝到服务器"
        return

    def proceed(self):
        try:
            self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'
            shutil.copyfile(pm.sceneName(), self.dialog.tank_file)
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


