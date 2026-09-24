# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.10
#
# Description: 
#
############################################

import traceback

import os
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的abc文件的路径和命名。"
        self.description = u"动态文件名为 <资产>.<关键词(任务名)>.<起始帧>_<结束帧>.abc。\n动态预览文件名为 <资产>.<关键词(任务名)>.<起始帧>_<结束帧>.proxy.abc。\n两者需要对应"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            l_dynamic_files = [self.dialog.w_publish_file.listWidget_dynamic.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_dynamic.count())]
            if len(l_dynamic_files) == 0:
                return u"还没有选择动态 (*.abc) 文件。"

            if len(l_dynamic_files) > 1:
                return u"只能选择1个动态 (*.abc) 文件。"

            l_proxy_files = [self.dialog.w_publish_file.listWidget_proxy.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_proxy.count())]
            if len(l_proxy_files) == 0:
                return u"还没有选择动态预览 (*.abc) 文件。"

            if len(l_proxy_files) > 1:
                return u"只能选择1个动态预览 (*.abc) 文件。"


            file_path = l_dynamic_files[0]
            if not os.path.isfile(file_path):
                return u"找不到文件: " + file_path

            dynamic_file = os.path.basename(file_path)
            if dynamic_file.lower() != dynamic_file:
                return u"文件名需要小写: " + file_path

            tokens = dynamic_file.split('.')
            if len(tokens) != 4:
                return u"动态文件名应该是 <资产>.<关键词(任务名)>.<起始帧>_<结束帧>.abc，一共四段: " + dynamic_file
            if tokens[0] != self.dialog.entity['name']:
                return u"动态文件名应该是 <资产>.<关键词(任务名)>.<起始帧>_<结束帧>.abc，以资产名" + self.dialog.entity['name'] + u"开头: " + dynamic_file

            l_frames = tokens[2].split('_')
            if len(l_frames) != 2:
                return u"动态文件名应该是 <资产>.<关键词(任务名)>.<起始帧>_<结束帧>.abc，第三段是连个数字用_连接: " + dynamic_file
            if not (l_frames[0].isdigit() and l_frames[1].isdigit()):
                return u"动态文件名应该是 <资产>.<关键词(任务名)>.<起始帧>_<结束帧>.abc，第三段是连个数字用_连接: " + dynamic_file

            self.dialog.dynamic_file = file_path

            file_path = l_proxy_files[0]
            if not os.path.isfile(file_path):
                return u"找不到文件: " + file_path

            proxy_file = os.path.basename(file_path)
            if proxy_file != dynamic_file[:-4] + '.proxy.abc':
                return u"动态预览文件名为 <资产>.<关键词(任务名)>.<起始帧>_<结束帧>.proxy.abc，现在不是: " + proxy_file

            self.dialog.proxy_file = file_path

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


