# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: John Su
#
# Date: 2014.1
#
# Description: As the description shows below
#
############################################

import os
import traceback
import re

# All system check classes will use StdCheck as the class name.





class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查所选cache目录的合法性"
        self.description = u"所选目录包含的版本号必须和指定版本号相符，而且必须包含.ass(.gz)或者.abc文件"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def __get_version(self, path):
        """
        return -1 if not successful
        """
        exp = r'\.v\d{3}'
        versions = re.findall(exp, path)
        if len(versions) is 0:
            return -1
        version = versions[0]
        if version == '':
            return -1
        version = int(version[-3:])
        return version

    def run_check(self):

        try:
            scene_ver = int(self.dialog.version_num)
            scene_ver_str = self.dialog.version_num

            n_cache_items = self.dialog.w_publish_file.listWidget_cache.count()
            if n_cache_items is 0:
                return u"没有选择cache。"

            for i in range(n_cache_items):
                cache_dir = self.dialog.w_publish_file.listWidget_cache.item(i).text()
                if cache_dir.endswith('/'):
                    cache_dir = cache_dir[:-1]

                # check pattern
                match = re.match(r'.*/plt/output/\w\d{5}\....\.\w*\.v\w{3}.*', cache_dir)
                if not match:
                    return u'路径格式不标准，表准的格式请参考：“<shot>/cfx/output/c10110.cfx.hair.v001/...”'

                # check version
                path_ver = self.__get_version(cache_dir)
                if path_ver is -1:
                    return u"路径中没有找到版本信息."
                if path_ver != scene_ver:
                    return cache_dir+u'的版本'+str(path_ver).zfill(3)+u'和目前版本 '+scene_ver_str+u' 不匹配.'

                # check if contains no .ass or .ass.gz
                ass_check = False
                for root, dirs, files in os.walk(cache_dir):
                    for f in files:
                        if f.endswith('.ass') or f.endswith('.ass.gz') or f.endswith('.abc') or f.endswith('.xml'):
                            ass_check = True
                            break
                    if ass_check is True:
                        break

                if not ass_check:
                    return u" " + cache_dir + u" 内没有找到任何.ass(.gz)或者.abc或者.xml文件。"

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


