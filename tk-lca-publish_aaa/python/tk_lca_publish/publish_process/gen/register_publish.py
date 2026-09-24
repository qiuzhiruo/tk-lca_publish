# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Create tank publish file entity
#
############################################

import traceback
import tank
import sys
import os
# from PySide import QtGui
import sgtk
from sgtk.platform.qt import QtCore, QtGui

# import getpass
# 
# if getpass.getuser() == "haojia":
#     import sys
#     sys.path.append("/home/haojia/Work/SoftWare/pycharm-2022.1.3/debug-eggs/pydevd-pycharm.egg_FILES/")
#     import pydevd_pycharm
#     import pydevd
#     pydevd.stoptrace()
#     pydevd_pycharm.settrace('localhost', port=1234, stdoutToServer=True, stderrToServer=True)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun数据库建立 Published File 。"
        self.description = u"在shotgun数据库建立 PublishedFile。该entity可以被之后的流程工具引用。"
        return

    def proceed(self):
        try:
            if sys.platform.startswith('win'):
                tank_file = self.dialog.tank_file.replace('/', '\\')
            else:
                tank_file = self.dialog.tank_file

            thumbnail_path = self.dialog.version_dir + '/preview/thumbnail.jpg'
            cmdStr = '"'+ self.dialog.rvio_path +'" ' + self.dialog.v_preview.replace('/', '\\') + " -o " + thumbnail_path
            os.system(cmdStr)

            args = {
                "tk": self.dialog.tk,
                "context": self.dialog.ctx,
                "comment": self.dialog.description,
                "task": self.dialog.ctx.task,
                "dependency_paths": self.dialog.dependency_paths,
                "published_file_type":self.dialog.published_file_type,
                "path": tank_file,
                "name": self.dialog.version_key,
                "version_number": int(self.dialog.version_num),
            }

            if os.path.isfile(thumbnail_path):
                args['thumbnail_path'] = thumbnail_path

            try:
                sg_data = tank.util.register_publish(**args)
                self.dialog.sg.update(sg_data['type'], sg_data['id'], {"code": self.dialog.version_name+'.ma', "version": self.dialog.v_info })
            except:
                self.dialog.print_log(traceback.format_exc(), txt_color = QtGui.QColor(255, 150, 30))

            # register Assembly Definition
            if not hasattr(self.dialog, 'assembly_definition'):
                print 'assembly_definition not found'
                return ""

            if not os.path.isfile(self.dialog.assembly_definition):
                print 'file not found', self.dialog.assembly_definition
                return ""

            if sys.platform.startswith('win'):
                path = self.dialog.assembly_definition.replace('/', '\\')
            else:
                path = self.dialog.assembly_definition

            args.update({
                "published_file_type": 'Maya Assembly',
                "path": path,
                "version_entity": self.dialog.v_info,
            })

            sg_data = tank.util.register_publish(**args)
            self.dialog.sg.update(sg_data['type'], sg_data['id'], {"code": self.dialog.version_name+'.ma'})
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
