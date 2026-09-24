# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2017.02
#
# Description: Copy publish files
#
############################################

import os
import traceback
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"将故事板艺术家提交的文件拷贝到版本文件夹，并重新命名。"
        return



    def proceed(self):
        try:
            # self.dialog.version_name
            # For art/edt department, the publish files and the preview files are the same.
            d_file_path_map = {}
            for file_path in self.dialog.l_preview_files:
                #shutil.copyfile(file_path, self.dialog.version_dir + '/' + os.path.basename(file_path))
                file_path = file_path.lower().replace('\\', '/')
                if not (file_path.endswith('.jpg') or file_path.endswith('.jpeg')):
                    continue
                dir_name = os.path.dirname(file_path)
                base_name = os.path.basename(file_path)
                alpha_name = base_name.lstrip('0123456789')
                if alpha_name == base_name:
                    path_map = file_path
                else:
                    digit = base_name[:-1*len(alpha_name)]
                    new_name = ('%05d' % (int(digit) + 1)) + alpha_name
                    path_map = dir_name + '/' + new_name

                d_file_path_map[path_map] = file_path

            l_dst = []
            for i, path_map in enumerate(sorted(d_file_path_map.keys())):
                src = d_file_path_map[path_map]
                dst = self.dialog.version_dir + '/' + self.dialog.version_name + ('.%04d.jpg' % (i+1))
                shutil.copyfile(src, dst)
                l_dst.append(dst)

            self.dialog.l_preview_files = l_dst

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


