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

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的Katana文件(*.katana, *.xml)的路径和命名。"
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
            self.dialog.katana_file=None

            if self.dialog.w_publish_file.checkBox.isChecked():
                return ''

            katana_file_path = str(self.dialog.w_publish_file.lineEdit_katana.text())

            if '/task/katana/' not in katana_file_path:
                return u"Katana 文件必须在srf task下的katana文件夹下"

            work_dir_path, katana_file= os.path.split(katana_file_path)

            template_key = "asset_publish"
            template_obj = self.dialog.tk.templates[template_key]
            l_paths = self.dialog.tk.paths_from_template(template_obj, self.dialog.ctx.as_template_fields(template_obj))
            publish_folder=None
            if l_paths:
                publish_folder=l_paths[0]
            if not publish_folder:
                return u'找不到对应的publish文件夹'

            tex_path = os.path.join(publish_folder , 'tex')
            if os.path.isdir(tex_path) and not os.access( tex_path ,os.W_OK):
                return u"Publish tex 文件夹权限未打开"

            if work_dir_path.endswith('/'):
                work_dir_path = work_dir_path[:-1]
            xml_dir_path = os.path.join(work_dir_path,'scene_graph_xml')

            if not os.path.isfile(katana_file_path) and katana_file_path != '':
                return u"找不到这个文件:\n  " + katana_file_path

            if not os.path.isdir(xml_dir_path) and xml_dir_path != '':
                return u"找不到这个文件夹:\n  " + xml_dir_path

            self.dialog.katana_file = katana_file_path
            self.dialog.xml_dir = xml_dir_path

            # Publish the preview only
            if katana_file_path == '' and xml_dir_path == '':
                return ''

            # Publish the look with the xml
            if katana_file_path == '' and xml_dir_path != '':
                return u"katana file和xml文件夹必须一起提交。"

            if katana_file_path != '' and xml_dir_path == '':
                return u"katana file和xml文件夹必须一起提交。"

            file_dir = os.path.dirname(katana_file_path)
            file_name = os.path.basename(katana_file_path)

            result = self.check_path(file_dir, 'Look file')
            if result != '':
                return result

            katana_file_name = self.dialog.entity['name']
            if katana_file_name != file_name.split('.')[0]:
                return u"katana文件名应该是: "+ katana_file_name+u'(.版本号)'

            result = self.check_path(xml_dir_path, 'Xml')
            if result != '':
                return result

            if not os.path.isfile(xml_dir_path + '/' + self.dialog.entity['name'] + '.xml'):
                return u"没有找到 " + xml_dir_path + '/' + self.dialog.entity['name'] + '.xml'

            l_files = os.listdir(xml_dir_path)
            for file_name in l_files:
                if file_name.endswith('.abc'):
                    return ''

            return u'scene_graph_xml文件夹内没有找到任何abc文件。'

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


