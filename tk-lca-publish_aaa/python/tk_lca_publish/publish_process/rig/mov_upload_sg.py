#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2025/11/10 15:56
# @File    : mov_upload_sg.py.py


import os
import traceback
import shutil
import pymel.core as pm
import maya.cmds as mc
import maya.OpenMaya as om
from assetsystem_sgl.tools.common.publish import profiling

class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"上传拍屏到 shotgun"
        self.description = u"上传拍屏到 shotgun"
        return

    def proceed(self):
        try:
            if mc.objExists("rig.char_type") and mc.getAttr("rig.char_type") == "Biped":
                try:
                    image_path = self.playblast()
                    self.dialog.sg.upload('Version', self.dialog.v_info['id'], image_path, "sg_uploaded_movie")
                except:
                    return ""
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


    def playblast(self):
        profiling.load_ani(publish=True)
        mov_filename = "{}/publish.mov".format(os.getenv("TEMP"))
        mov_filename = mc.playblast(fp=4, clearCache=1, format='qt', sequenceTime=0, showOrnaments=1, percent=100,
                     filename=mov_filename, viewer=0, forceOverwrite=1, quality=100, widthHeight=(1920, 1080),
                     compression="H.264")
        profiling.clear_ani()
        return mov_filename
