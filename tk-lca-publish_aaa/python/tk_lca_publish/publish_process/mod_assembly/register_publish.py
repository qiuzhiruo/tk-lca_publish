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
            for asset_name in self.dialog.d_assets_info.keys():
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                asset = self.dialog.d_assets_info[asset_name]['asset']
                task = self.dialog.d_assets_info[asset_name]['task']
                version_name = self.dialog.d_assets_info[asset_name]['version_name']
                tank_file = self.dialog.d_assets_info[asset_name]['tank_file']
                thumbnail_path = self.dialog.d_assets_info[asset_name]['thumbnail']
                v_info = self.dialog.d_assets_info[asset_name]['v_info']
                assembly_definition = self.dialog.d_assets_info[asset_name]['assembly_file']

                if sys.platform.startswith('win'):
                    tank_file = tank_file.replace('/', '\\')

                #cmdStr = '"'+ self.dialog.rvio_path +'" ' + self.dialog.v_preview.replace('/', '\\') + " -o " + thumbnail_path
                #os.system(cmdStr)

                args = {
                    "tk": self.dialog.tk,
                    "context": self.dialog.ctx,
                    "comment": self.dialog.description,
                    "task": task,
                    "dependency_paths": [],
                    "published_file_type":self.dialog.published_file_type,
                    "path": tank_file,
                    "name": version_name[:-5],
                    "version_number": int(version_name[-3:]),
                }

                if os.path.isfile(thumbnail_path):
                    args['thumbnail_path'] = thumbnail_path

                try:
                    sg_data = tank.util.register_publish(**args)
                    self.dialog.sg.update(sg_data['type'], sg_data['id'], {"code": version_name+'.ma', "version": v_info, "entity":asset})
                except:
                    self.dialog.print_log(traceback.format_exc(), txt_color = QtGui.QColor(255, 150, 30))

                # register Assembly Definition
                if not os.path.isfile(assembly_definition):
                    print 'file not found', assembly_definition
                    return ""

                if sys.platform.startswith('win'):
                    path = assembly_definition.replace('/', '\\')
                else:
                    path = assembly_definition

                args.update({
                    "published_file_type": 'Maya Assembly',
                    "path": path,
                    "version_entity": v_info,
                })

                sg_data = tank.util.register_publish(**args)
                self.dialog.sg.update(sg_data['type'], sg_data['id'], {"code": version_name+'.ma', "entity":asset})
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


