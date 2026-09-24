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

import traceback

import os
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"从无版本号文件夹删除选中的图片。"
        self.description = u"从无版本号文件夹删除选中的图片"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            image_num=self.dialog.image_layout.count()
            del_image_list=[]
            for i in range(image_num):
                image_item=self.dialog.image_layout.itemAt(i)
                image_item_wedget=image_item.widget()
                if image_item_wedget.isDel:
                    del_image_list.append(image_item_wedget.image_path)

            for image_icon_path in del_image_list:
                image_path=os.path.join(os.path.dirname(image_icon_path)[:-5],os.path.basename(image_icon_path)[:-4])
                os.system('rm '+image_icon_path)
                os.system('rm '+image_path)

                self.dialog.print_log('del image path :'+image_path)

            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



