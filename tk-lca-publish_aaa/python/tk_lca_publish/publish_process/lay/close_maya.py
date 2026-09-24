# -*- coding:utf-8 -*-

import os
import traceback
import math
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"关闭maya"
        self.description = u"保存场景，关闭maya"
        return

    def proceed(self):
        try:
            import maya.cmds as cmds
            cmds.file( save=True, force=True )
            cmds.quit(force=True)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


