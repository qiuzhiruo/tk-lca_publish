# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Zhao Cong
#
# Date: 2014.04
#
# Description: As the description shows below
#
############################################

import os
import traceback
from pymel.core import *
import shutil


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"保存后升文件版本号"
        self.description = u"将场景文件保存，并且升级版本号"#(到%s)"%self.__next_ver()

    def __next_ver(self):
        return 'v'+str(int(self.dialog.version_num)+1).zfill(3)
        
    def __get_version(self, path):
        exp = r'hair.v\d{3}'
        versions = re.findall(exp, path)
        if len(versions) is 0:
            return -1
        version = versions[0]
        if version == '':
            return -1
        version = int(version[-3:])
        return version

    def proceed(self):
        try:
            runtime.SaveScene()

            # rename
            scene_name = sceneName()
            old_str = scene_name[-8:-2]
            new_str = '.' + self.__next_ver() + '.'
            

            new_name =os.path.basename(scene_name).replace(old_str, new_str) #os.path.dirname(scene_name)+'/'+
            if new_name == scene_name:
                return u'重命名出错:'+new_name
            saveAs(new_name)
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


