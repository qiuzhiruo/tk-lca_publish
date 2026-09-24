# -*- coding:utf-8 -*-

import os
import traceback
import shutil

import maya.cmds as cmds

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"隐藏不用于渲染的网格"
        self.description = u"隐藏下列网格：1.eyeelse_baffle_plate"
        return

    def proceed(self):
        try:
            if cmds.objExists('eyeelse_baffle_plate'):
                cmds.hide('eyeelse_baffle_plate')
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description