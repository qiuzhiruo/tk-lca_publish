# -*- coding:utf-8 -*-

import os
import traceback
import shutil

import pymel.core as pm


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"自动升级一个版本"
        self.description = u"自动升级一个版本"
        return


    def proceed(self):
        try:
            ma_file = pm.sceneName()
            version_up = ma_file[:-7] + 'v' + format( int(self.dialog.version_num)+1, '#03' ) + '.ma'

            # version up
            try:
                shutil.copyfile( ma_file, version_up )
            except:
                return u"升级版本失败: "+version_up

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


