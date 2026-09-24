# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.06
#
# Description: Upload version previews to shotgun
#
############################################

import os
import sys
import traceback
import shutil
import subprocess
import getpass


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"上传版本预览"
        self.description = u"为shotgun提交版本直接上传或者将图片序列转换一个视频文件(*.mov)作为版本预览，会帮助其他艺术家快速了解这个版本。"
        return

    def proceed(self):
        try:
            for data in self.dialog.shots_preview_data:
                # create preview folder
                preview_dir = os.path.join(data['version_dir'], 'preview')
                if not os.path.isdir(preview_dir):
                    os.makedirs(preview_dir)

                data['version_preview'] = os.path.join(preview_dir, data['version_name']+'.mov').replace('\\', '/')
                shutil.copyfile(data['preview'], data['version_preview'])

                version_preview_rv = data['version_preview'].replace('\\', '/')
                version_preview_rv = version_preview_rv.replace('Z:/', '${RV_PATHSWAP_ROOT}/')
                version_preview_rv = version_preview_rv.replace('/mnt/proj/', '${RV_PATHSWAP_ROOT}/').replace('\\', '/')
                self.dialog.sg.update('Version',
                                      data['version_info']['id'],
                                      {'sg_path_to_movie':version_preview_rv})
                self.dialog.sg.upload('Version',
                                      data['version_info']['id'],
                                      data['version_preview'],
                                      "sg_uploaded_movie")
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

