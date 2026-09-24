# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.06
#
# Description:
#
############################################


import traceback
import tank
import sys
import os
# from PySide import QtGui
import sgtk
from sgtk.platform.qt import QtCore, QtGui

import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun数据库建立相机信息 。"
        self.description = u"在shotgun数据库建立 PublishedFile。该entity可以被之后的流程工具引用。"
        return

    def write_log(self, content):
        try:
            import proc.log_publish_process as lpp
            reload(lpp)
            current_file = pm.sceneName().replace('\\','/')
            publish_log_dir = os.path.dirname(current_file) + '/publish_log'
            if not os.path.exists(publish_log_dir):
                os.makedirs(publish_log_dir)
            log_file = publish_log_dir + '/' + os.path.basename(current_file)[:-3]+'.log.txt'
            log_file = log_file.replace('\\', '/')
            if not os.path.exists(log_file):
                op = open(log_file, 'w')
                op.close()
            lpp.log(log_file, content)
        except:
            self.dialog.print_log(traceback.format_exc())

    def proceed(self):
        try:
            log = 'register_camera.py\n'
            self.write_log('register_camera.py\n')

            self.dialog.is_camera_published = False
            cam_file = self.dialog.cam_dir + '/' + self.dialog.entity['name'] + '_cam_anim.ma'
            if sys.platform.startswith('win'):
                cam_file = cam_file.replace('/', '\\')

            if  not os.path.isfile(cam_file):
                log += 'self.dialog.cam_dir is empty because the camera dir or cam_file does not exist, no need to register camera\n'
                log += 'self.dialog.cam_dir: ' + self.dialog.cam_dir + '\n'
                log += 'cam_file: ' + cam_file + '\n'
                self.write_log(log)
                return ''

            args = {
                "tk": self.dialog.tk,
                "context": self.dialog.ctx,
                "comment": self.dialog.description,
                "task": self.dialog.ctx.task,
                "dependency_paths": [],
                "published_file_type": 'Maya Camera',
                "path": cam_file,
                "name": self.dialog.entity['name']+'.cam.camera',
                "version_number": int(self.dialog.cam_dir[-3:]),
            }
            thumbnail_path = self.dialog.version_dir + '/preview/thumbnail.jpg'
            if os.path.isfile(thumbnail_path):
                args['thumbnail_path'] = thumbnail_path
            try:
                sg_data = tank.util.register_publish(**args)
                self.dialog.sg.update(sg_data['type'], sg_data['id'], {"code": os.path.basename(self.dialog.cam_dir)+'.ma', "version": self.dialog.v_info })
                self.dialog.is_camera_published = True
                log += 'camera file: '+cam_file+'\n'
                log += 'name: '+self.dialog.entity['name']+'.cam.camera\n'
                log += 'version_number: '+self.dialog.cam_dir[-3:]+'\n'
                log += 'set self.dialog.is_camera_published to True\n'
            except:
                self.dialog.print_log(traceback.format_exc(), txt_color = QtGui.QColor(255, 150, 30))
                log += 'failed to register camera\n' + traceback.format_exc()+'\n'
                self.write_log(log)
                return traceback.format_exc()
            self.write_log(log)

            return ""

        except:
            self.write_log(str(traceback.format_exc()) + '\n')
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


