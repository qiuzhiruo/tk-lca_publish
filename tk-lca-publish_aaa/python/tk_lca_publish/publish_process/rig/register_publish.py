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
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun数据库建立 Published File 。"
        self.description = u"在shotgun数据库建立 PublishedFile。该entity可以被之后的流程工具引用。"
        return

    def proceed(self):
        try:
            #print '===rigister_publish==='
            #print self.dialog.anim_file
            if sys.platform.startswith('win'):
                tank_file = self.dialog.tank_file.replace('/', '\\')
                anim_file = self.dialog.anim_file.replace('/', '\\')+'.ma'
            else:
                tank_file = self.dialog.tank_file
                anim_file = self.dialog.anim_file+'.ma'

            thumbnail_path = self.dialog.version_dir + '/preview/thumbnail.jpg'
            cmdStr = '"'+ self.dialog.rvio_path +'" ' + self.dialog.v_preview.replace('/', '\\') + " -o " + thumbnail_path
            os.system(cmdStr)

            tank_file = tank_file[:-3] + '.mb'
            anim_file = anim_file[:-3] + '.mb'

            args = {
                "tk": self.dialog.tk,
                "context": self.dialog.ctx,
                "comment": self.dialog.description,
                "path": tank_file,
                "name": self.dialog.version_key,
                "version_number": int(self.dialog.version_num),
                "task": self.dialog.ctx.task,
                "dependency_paths": [],
                "published_file_type":"Tech Rig",
            }

            if os.path.isfile(thumbnail_path):
                args['thumbnail_path'] = thumbnail_path

            # Change Tank Publish File Name

            try:
                sg_data = tank.util.register_publish(**args)
                self.dialog.sg.update(sg_data['type'], sg_data['id'], {'code': (self.dialog.version_name+'.mb'), "version": self.dialog.v_info })
            except:
                self.dialog.print_log(traceback.format_exc(), txt_color = QtGui.QColor(255, 150, 30))


            #rigister anim rig file
            args = {
                "tk": self.dialog.tk,
                "context": self.dialog.ctx,
                "comment": self.dialog.description,
                "path": anim_file,
                "name": self.dialog.version_key,
                "version_number": int(self.dialog.version_num),
                "task": self.dialog.ctx.task,
                "dependency_paths": [],
                "published_file_type":"Anim Rig",
            }

            if os.path.isfile(thumbnail_path):
                args['thumbnail_path'] = thumbnail_path

            # Change Tank Publish File Name

            try:
                sg_data = tank.util.register_publish(**args)
                self.dialog.sg.update(sg_data['type'], sg_data['id'], {'code': (self.dialog.version_name+'.mb'), "version": self.dialog.v_info })
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


