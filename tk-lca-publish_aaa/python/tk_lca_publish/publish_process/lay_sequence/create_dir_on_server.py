# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.06
#
# Description: Create version dir on the server
#
############################################

import os
import traceback

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在服务器上建立版本文件夹"
        self.description = u"在服务器上建立版本文件夹。"
        return


    def proceed(self):
        try:
            self.dialog.version_dir = self.dialog.publish_root + '/' + self.dialog.version_name
            if not os.path.isdir(self.dialog.version_dir):
                os.makedirs(self.dialog.version_dir)

            for data in self.dialog.shots_preview_data:
                data['version_name'] = '%s.lay.rough_layout.v%s' % (data['shot_info']['code'],
                                                                    self.dialog.version_num)
                data['version_dir'] = os.path.join(data['publish_root'],
                                                   data['version_name'])
                if not os.path.isdir(data['version_dir']):
                    os.makedirs(data['version_dir'])

                import production.make_extra_data_dirs.make_extraData_dirs as medd
                # 创建 lay 的 extra_data_dirs, 在最开始创建，避免权限问题22
                medd.make_rough_lay_extra_data_dirs(data['version_dir'])

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

