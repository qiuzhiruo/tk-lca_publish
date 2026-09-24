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
        self.description = u"所选目录包含的版本号必须和指定版本号相符,如果是publish过的资产，则文件夹内必须要有abc"
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
                cache_dir = cache_dir.rstrip('/')

                # if cache_dir is from publish
                if '/publish/' in cache_dir:
                    if not os.path.isdir(cache_dir):
                        return u'%s不是abc而且不是文件夹.'%cache_dir
                    continue

                # check pattern
                match = re.match(r'.*/efx/output/\w\d{5}\....\.\w*\.v\w{3}.*', cache_dir) or \
                        re.match(r'.*/efx/img/\w\d{5}\....\.\w*\.v\w{3}.*', cache_dir)
                if not match:
                    return u'路径格式不标准，表准的格式请参考：“<shot>/efx/<output|img>/c10110.efx.water.v001”'

                # check version
                path_ver = self.__get_version(cache_dir)
                if path_ver is -1:
                    return u"路径中没有找到版本信息."
                if path_ver != scene_ver:
                    return cache_dir+u'的版本'+str(path_ver).zfill(3)+u'和目前版本 '+scene_ver_str+u' 不匹配.'

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


