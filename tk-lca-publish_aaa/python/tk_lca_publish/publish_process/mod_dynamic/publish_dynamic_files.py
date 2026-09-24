# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.10
#
# Description: Copy alembic files
#
############################################

import os
import traceback
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝abc文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的abc文件拷贝到版本文件夹。"
        return


    def proceed(self):
        try:

            if not os.path.isdir(self.dialog.version_dir + '/scene_graph_xml' ):
                os.makedirs(self.dialog.version_dir + '/scene_graph_xml' )

            tokens = os.path.basename(self.dialog.dynamic_file).split('.')
            tokens[1] = self.dialog.task['name'].lower()
            new_name = '.'.join(tokens)

            shutil.copyfile(self.dialog.dynamic_file, self.dialog.version_dir + '/scene_graph_xml/' + new_name)
            shutil.copyfile(self.dialog.proxy_file, self.dialog.version_dir + '/scene_graph_xml/proxy.abc')

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


