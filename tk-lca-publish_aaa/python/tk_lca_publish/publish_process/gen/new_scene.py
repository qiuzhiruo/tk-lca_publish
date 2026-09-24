# -*- coding:utf-8 -*-

import os
import traceback
import math
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"新建场景(Untilted)"
        self.description = u"新建场景"
        return

    def proceed(self):
        try:
            import maya.cmds as cmds
            try:
                cmds.file( newFile=True, force=True )
            except:
                print traceback.format_exc()

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


