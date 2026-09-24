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

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog

        self.check_name = u"检查有没有scenegraphxml。"
        self.description = u"提交时需要在task/katana下有scenegraphxml 。"
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
            katana_file_path = FarmAPI.GetKatanaFileName()

            if katana_file_path == '' :
                return ''
            
            if katana_file_path.split('/')[6] == 'efx':
                return ''

            work_dir_path, katana_file= os.path.split(katana_file_path)
            self.dialog.katana_file = katana_file_path

            if work_dir_path.endswith('/'):
                work_dir_path = work_dir_path[:-1]
            xml_dir_path = os.path.join(work_dir_path,'scene_graph_xml')

            self.dialog.xml_file= None
            self.dialog.xml_dir = None
            Katana_file_path = FarmAPI.GetKatanaFileName()
            tokens = Katana_file_path.split('/')
            cur_proj = tokens[4]

            if os.path.isdir(xml_dir_path) and os.listdir(xml_dir_path):
                self.dialog.xml_dir = xml_dir_path
                result = self.check_path(xml_dir_path, 'Xml')
                if result != '':
                    self.dialog.print_log(result,txt_color=QtGui.QColor(255, 150, 30))
                self.dialog.xml_file=xml_dir_path + '/' + self.dialog.entity['name'] + '.xml'
                if not os.path.isfile(self.dialog.xml_file):
                    self.dialog.print_log( u"没有找到 " + xml_dir_path + '/' + self.dialog.entity['name'] + '.xml',\
                                           txt_color=QtGui.QColor(255, 150, 30))
                has_abc = False
                has_uv = False
                l_files = os.listdir(xml_dir_path)
                for file_name in l_files:
                    if file_name.endswith('.uv'):
                        with open(os.path.join(xml_dir_path, file_name),'r') as f:
                            content = f.readlines()
                        if content:
                            has_uv = True
                            ProjectStr = r"/projects/(\w{3})/asset/(\w+)/(\w+)/(\w{3})/"
                            ProjectStrC = re.compile(ProjectStr)
                            results = ProjectStrC.findall(content[0].replace("\\", "/"))
                            uv_proj = results[0][0]
                            if uv_proj != cur_proj:
                                return u'使用的不是最新xml,若为复用资产,需要重出,不可直接复制:'+xml_dir_path
                    if file_name.endswith('.abc'):
                        has_abc=True

                if not has_uv:
                    return u'scene_graph_xml文件夹中没有uv,请重出:'+xml_dir_path
                if not has_abc:
                    return u'scene_graph_xml文件夹中没有abc,请重出:'+xml_dir_path
            else:
                return u'没有找到scene_graph_xml文件夹，或者文件夹下没有任何文件'
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


