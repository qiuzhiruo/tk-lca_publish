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
        self.check_name = u"Asset路径检查"
        self.description = u"检查所选Asset路径的合法性"
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
            paths = []
            for i in range(self.dialog.w_publish_file.listWidget_cache.count()):
                paths.append(self.dialog.w_publish_file.listWidget_cache.item(i).text())

            # extensions = []
            # for p in paths:
            #     extensions.append(p.split('.')[-1])
            # if len(set(extensions)) is not len(extensions):
            #     return u'同一种扩展名只包含一个文件'

            error_file = False

            for p in paths:
                if 'CompName:' in p:
                    continue
                if len(p.split())>=2:
                    return (u'路径中不能包含空格 '+p)
                component_name=p.split('/')[-3]
                extension=p.split('.')[-1]
                if os.path.isdir(p):
                    continue

                elif extension in ['abc','nk','tif'] and os.path.isfile(p):
                    continue

                elif extension in ['vdb','exr']:
                    if os.path.isfile(p):
                        continue
                    else:
                        folder=os.path.dirname(p)
                        file_sp=os.path.basename(p).split('-')
                        if os.path.isfile(os.path.join(folder,file_sp[0])) and \
                            os.path.isfile(os.path.join(folder,file_sp[-1])):
                            continue
                    if extension=='vdb':
                        if not any(['smoke' in comp_name, 'dust' in comp_name,'fire' in comp_name]):
                            return u'元素名称中必须包含smoke,dust,fire关键字'
                        look_file=os.path.join(os.path.dirname(abs_path),comp_name+'.klf')
                        if not look_file or not os.path.isfile(look_file):
                            return ('Can not find look file for vdb'+component_name)

                error_file=True

            if error_file:
                return u'请选择文件，或者确保列表中有文件，而不全都是文件夹'

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


