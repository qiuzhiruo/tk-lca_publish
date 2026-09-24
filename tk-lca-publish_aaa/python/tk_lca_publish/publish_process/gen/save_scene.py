# -*- coding:utf-8 -*-

import os
import traceback
import pymel.core as pm
import math
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"保存场景"
        self.description = u"保存场景"
        return

    def proceed(self):
        try:
            import maya.cmds as cmds
            try:
                cmds.file( save=True, force=True )
                self.dialog.work_file = pm.sceneName()
            except:
                print traceback.format_exc()

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


