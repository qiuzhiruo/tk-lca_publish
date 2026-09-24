# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.10
#
# Description: Create tank publish file entity
#
############################################
import traceback
import sys
import os

import tank
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun数据库为镜头建立 Published File 。"
        self.description = u"在shotgun数据库建立 PublishedFile。该entity可以被之后的流程工具引用。"
        return

    def proceed(self):
        try:
            # Register Scene
            thumbnail_path = self.dialog.version_dir + '/preview/thumbnail.jpg'
            cmdStr = '"'+ self.dialog.rvio_path +'" ' + self.dialog.v_preview + " -o " + thumbnail_path
            os.system(cmdStr)

            path = os.path.join(self.dialog.version_dir, os.path.basename(pm.system.sceneName()))
            tank_file = os.path.normpath(path)
            
            args = {
                "tk": self.dialog.tk,
                "context": self.dialog.ctx,
                "comment": self.dialog.description,
                "task": self.dialog.ctx.task,
                "dependency_paths": [],
                "published_file_type":self.dialog.published_file_type,
                "version_number": int(self.dialog.version_num),
                'version_entity': self.dialog.v_info,
            }
            if os.path.isfile(thumbnail_path):
                args['thumbnail_path'] = os.path.normpath(thumbnail_path)

            for data in self.dialog.actions_data:
                # args.update(name=self.dialog.version_key + '.' + data['name'],
                #             path=data['path'])
                args.update(name=self.dialog.version_key+'.'+data['name'],
                            path=tank_file)
                tank.util.register_publish(**args)
            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
