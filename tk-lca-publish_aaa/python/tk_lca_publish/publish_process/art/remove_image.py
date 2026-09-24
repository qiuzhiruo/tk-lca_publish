# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: YU HuaZhuo
#
# Date: 2017.02
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
        self.process_name = u"从无版本号文件夹删除选中的图片"
        self.description = u"从无版本号文件夹删除选中的图片。"
        return

    def proceed(self):
        try:

            image_num = self.dialog.image_layout.count()
            del_image_list = []
            for i in range(image_num):
                image_item = self.dialog.image_layout.itemAt(i)
                image_item_wedget = image_item.widget()
                if image_item_wedget.isDel:
                    del_image_list.append(image_item_wedget.image_path)

            if len(del_image_list) > 0:
                image_icon_dir = os.path.dirname(del_image_list[0])
                image_dir = os.path.dirname(image_icon_dir)
                backup_dir = os.path.join(image_dir, 'backup')
                self.dialog.print_log('del image path backup_dir :' + backup_dir)
                if not os.path.isdir(backup_dir):
                    os.mkdir(backup_dir, 0777)

                for image_icon_path in del_image_list:
                    image_path = os.path.join(image_dir, os.path.basename(image_icon_path)[:-4])

                    new_image_name = image_path[:-3]+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+image_path[-4:]
                    self.dialog.print_log('del image path src:' + image_path)
                    self.dialog.print_log('del image path dst:' + new_image_name)
                    os.rename(image_path, os.path.join(backup_dir, os.path.basename(new_image_name)))
                    os.remove(image_icon_path)


            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
