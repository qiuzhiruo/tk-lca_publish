# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.11
#
# Description: As the description shows below
#
############################################

import os
import traceback

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查动画Cache文件。"
        self.description = u"Cache文件夹内应该有一个和资产同名的xml文件;应该有至少一个abc文件。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            for i in range(self.dialog.w_publish_file.listWidget_cache.count()):
                cache_dir = self.dialog.w_publish_file.listWidget_cache.item(i).text()
                if cache_dir.endswith('/'):
                    cache_dir = cache_dir[:-1]

                dir_name = os.path.basename(cache_dir)
                xml_path = cache_dir + '/' + dir_name + '.xml'
                if not os.path.isfile(xml_path):
                    return u"没有找到Cache需要的xml文件: "+xml_path

                l_files = os.listdir(cache_dir)
                abc_chk = False
                for file_name in l_files:
                    if file_name.endswith('.abc'):
                        abc_chk = True

                if not abc_chk:
                    return u"Cache文件夹 " + cache_dir + u" 内没有找到任何abc文件。"

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


