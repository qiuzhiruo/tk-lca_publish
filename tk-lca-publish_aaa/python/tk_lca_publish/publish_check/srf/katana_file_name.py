# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check shtogun data
#
############################################

import traceback

import os
import re
from Katana import FarmAPI
import sgtk
from sgtk.platform.qt import QtCore, QtGui
from Katana import KatanaFile

TXT_DEFAULT = QtGui.QColor(200, 200, 200)
TXT_ORANGE = QtGui.QColor(255, 150, 30)
TXT_RED = QtGui.QColor(255, 50, 50)
TXT_BLUE = QtGui.QColor(150, 150, 255)
TXT_WHITE = QtGui.QColor(255, 255, 255)

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的Katana文件(*.katana)的路径和命名。"
        self.description = u"scene graph xml必须和Katana同时提交。Katana文件名由资产名+.katana组成。scene_graph_xml文件夹内包含xml文件和abc文件。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def check_path(self, path, key):
        p = re.compile("[\w\.]*$")
        tokens = path.replace(":", "\\").replace("/", "\\").split("\\")
        for token in tokens:
            if not p.match(token):
                return key + u" 各级文件夹需要由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成:\n  " + path

        return ''


    def run_check(self):

        try:
            if int(self.dialog.w_publish_file.checkBox.isChecked()):
                return ''

            katana_file_path = FarmAPI.GetKatanaFileName()

            if '/task/katana/' not in katana_file_path:
                return u"Katana 文件必须在srf task下的katana文件夹下"

            template_key = "asset_publish"
            template_obj = self.dialog.tk.templates[template_key]
            l_paths = self.dialog.tk.paths_from_template(template_obj, self.dialog.ctx.as_template_fields(template_obj))
            publish_folder=None
            if l_paths:
                publish_folder=l_paths[0]
            if not publish_folder:
                return u'找不到对应的publish文件夹'

            tex_path = os.path.join(publish_folder, 'publish/tex')

            if os.path.isdir(tex_path) and not os.access( tex_path ,os.W_OK):
                return u"Publish tex 文件夹权限未打开"


            file_name = os.path.basename(katana_file_path)
            asset_name = self.dialog.entity['name']
            if asset_name != file_name.split('.')[0]:
                return u"katana文件名应该是: "+ asset_name+u'(.版本号)'

            try:
                KatanaFile.Save(katana_file_path)
            except:
                self.dialog.print_log(u'试图保存当前场景,没有成功,可忽略。\n',txt_color=TXT_BLUE)

            self.dialog.katana_file = katana_file_path

            return''
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


