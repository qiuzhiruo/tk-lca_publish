# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yu HuaZhuo
#
# Date: 2017.02
#
# Description: Get shtogun data
#
############################################

import traceback
import os
import re
from sgtk.platform.qt import QtCore, QtGui

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检测无版本号的文件夹。"
        self.description = u"整理一个包含完整图片的文件方便下游使用。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def add_image(self,publish_no_version,image_list):

        for image in image_list:
            image_path=os.path.join(publish_no_version,'icon',image+'.png')
            if os.path.isfile(image_path) and image_path not in self.dialog.no_version_image_list:
                self.ui_ThxWidgetItem=self.dialog.ui_ThxWidgetItem(image_path=image_path)
                self.dialog.image_layout.addWidget(self.ui_ThxWidgetItem)
                self.dialog.no_version_image_list.append(image_path)

    def run_check(self):
        try:
            # This is tricky, any input from the GUI need to consider the possible issue from Chinese letters
            publish_root=self.dialog.publish_root
            version_name_qtstr = self.dialog.version_key.decode("utf-8")
            publish_no_version=os.path.join(publish_root,version_name_qtstr+'.v000')
            #self.dialog.print_log('publish_no_version : '+str(publish_no_version))
            if os.path.isdir(publish_no_version):
                image_list=os.listdir(publish_no_version)
                if len(image_list)>0:
                    self.add_image(publish_no_version,image_list)
            else:
                os.makedirs(publish_no_version,0777)


            return ""

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

