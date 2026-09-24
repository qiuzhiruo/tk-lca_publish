# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2016.01
#
# Description: Scan scene to get dependency paths
#
############################################

import traceback
import tank
import sys
import os
# from PySide import QtGui
import sgtk
from sgtk.platform.qt import QtCore, QtGui
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"扫描场景以获取依赖的上游文件路径 。"
        self.description = u"扫描场景以获取依赖的上游文件路径，供建立publishedFile时使用。"
        return

    def proceed(self):
        try:
            engine = self.dialog._app.engine
            app = engine.apps.get("tk-multi-breakdown")
            if app:
                items = app.execute_hook_method("hook_scene_operations", "scan_scene")
                for item in items:
                    path = item['path']
                    if path not in self.dialog.dependency_paths:
                        self.dialog.dependency_paths.append(path)
            else:
                self.dialog.print_log('Breakdown app not found in current engine, skipping...')
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
