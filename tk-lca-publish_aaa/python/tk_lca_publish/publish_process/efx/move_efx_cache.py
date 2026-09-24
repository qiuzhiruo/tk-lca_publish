# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: John Su
#
# Date: 2013.11
#
# Description: As the description shows below
#
############################################

import os
import traceback
import shutil
import re


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"复制Cache"
        self.description = u"复制所选cache目录到publish文件夹，如果cache位于publish文件夹，则直接使用symlink"

    def output(self, msg):
        self.dialog.print_log(msg)

    def proceed(self):
        try:
            
            #scene_name = os.path.basename(sceneName())[:-3]
            for i in range(self.dialog.w_publish_file.listWidget_cache.count()):
                dir_path = self.dialog.w_publish_file.listWidget_cache.item(i).text().rstrip('/')

                if '/publish/' in dir_path:
                    if '/shot/' in dir_path:
                        self.output(u'Warning: 最好不要publish shot下的cache, 而是从asset下pa.')

                    # TODO: support all media types. ABC only now.
                    abc_path = None
                    for f in os.listdir(dir_path):
                        if f.endswith('.abc'):
                            abc_path = f
                            break

                    if abc_path:
                        #if '/asset/' in dir_path:
                        #    asset_name = abc_path.split('.')[-1]
                        asset_name = '.'.join(abc_path.split('.')[:-1])
                        target_path = os.path.join(self.dialog.version_dir, asset_name, 'abc', abc_path)
                    else:   # impossible
                        self.output(i)
                        return u'奇怪的事情发生了，请告知TD'

                    target_folder = os.path.dirname(target_path)
                    if os.path.exists(target_folder):
                        shutil.rmtree(target_folder)
                    os.makedirs(target_folder)
                    os.symlink(os.path.join(dir_path, abc_path), target_path)

                else:
                    exp = r'/[\d\w]*\..*\..*\.v\d{3}'
                    re_result = re.findall(exp, dir_path)
                    if len(re_result) is 0:
                        return dir_path+u'不标准，请参考格式：<shot_dir>/efx/<output|img>/f74070.efx.snow.v007/snowball/abc/snowball.abc'
                    ver_path = re_result[0][1:]

                    sub_path = dir_path.split(ver_path)[1]
                    target_dir = self.dialog.version_dir +'/'+ sub_path

                    if os.path.exists(target_dir):
                        shutil.rmtree(target_dir)

                    os.makedirs(target_dir)

                    self.output(target_dir)   #debug
                    for f in os.listdir(dir_path):
                        src = dir_path+'/'+f
                        dst = self.dialog.version_dir +'/'+ sub_path+ '/'+f

                        if os.path.isdir(src):
                            shutil.copytree(src, dst)
                        elif os.path.isfile(src):
                            dst_dir = os.path.dirname(dst)
                            if not os.path.isdir(dst_dir):
                                os.makedirs(dst_dir)
                            shutil.copy2(src, dst)
                        else:
                            return u'路径不存在:'+src

            return ""
        except:
            self.output(u'publish错误，请检查路径是否符合标准.')
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


