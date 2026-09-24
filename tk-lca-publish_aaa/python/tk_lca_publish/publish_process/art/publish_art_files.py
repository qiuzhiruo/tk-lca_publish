# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Copy publish files
#
############################################

import os
import traceback
import shutil
import datetime


# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件拷贝到版本文件夹。"
        return

    def proceed(self):
        try:
            # For art/edt department, the publish files and the preview files are the same.
            for file_path in self.dialog.l_preview_files:
                version_name = os.path.basename(self.dialog.version_dir)
                file_path = unicode(file_path)
                shutil.copyfile(file_path, self.dialog.version_dir + '/' + os.path.basename(file_path))
                all_image_folder = self.dialog.version_dir[:-4] + 'v000'
                if not os.path.isdir(all_image_folder):
                    os.makedirs(all_image_folder, 0777)

                new_file_path = all_image_folder + '/' + version_name+'.'+os.path.basename(file_path)
                if os.path.isfile(new_file_path):
                    backup_dir = os.path.join(all_image_folder, 'backup')
                    if not os.path.isdir(backup_dir):
                        os.makedirs(backup_dir, 0777)

                    backup_image_name = new_file_path[:-3]+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+new_file_path[-4:]
                    os.rename(new_file_path, os.path.join(backup_dir, os.path.basename(backup_image_name)))
                if 'delete_image' in file_path:
                    continue
                shutil.copyfile(file_path, new_file_path)

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
