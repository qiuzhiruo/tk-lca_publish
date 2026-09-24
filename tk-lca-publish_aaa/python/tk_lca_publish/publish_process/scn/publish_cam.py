# -*- coding:utf-8 -*-

import os
import traceback
import shutil
import maya.cmds as cmds
import pymel.core as pm

class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"发布相机"
        self.description = u"将场景中cam组下的相机，导出到proj盘第一版文件夹里面"
        return

    def export_cam(self):
        cam_dir = os.path.join(self.dialog.version_dir, 'camera')
        if not os.path.exists(cam_dir):
            os.makedirs(cam_dir)
        cam_file = os.path.join(cam_dir, 'camera.ma')
        cmds.file(cam_file, exportSelected=True, force=True, typ='mayaAscii')
        cmds.file( save=True, force=True )
        work_cam_file = os.path.join(os.path.dirname(pm.sceneName()), 'camera.ma')
        cmds.file(work_cam_file, exportSelected=True, force=True, typ='mayaAscii')

    def proceed(self):

        if cmds.objExists('|cam'):
            cmds.select('|cam')
            self.export_cam()
            cmds.delete('|cam')
        elif cmds.objExists('|camera'):
            cmds.select('|camera')
            self.export_cam()
            cmds.delete('|camera')

        return ""


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


