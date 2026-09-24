# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
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
            #print 'create dir on server.py'
            #print self.dialog.version_dir
            if not os.path.isdir(self.dialog.version_dir):
                os.makedirs(self.dialog.version_dir)

            if not os.path.isdir(self.dialog.version_dir + '/preview'):
                os.makedirs(self.dialog.version_dir + '/preview')
                if '/yzc/' in self.dialog.version_dir.replace('\\', '/'):
                    os.chmod(self.dialog.version_dir + '/preview', 0777)

            if self.dialog.step['name'] in ['ani', 'flo']:
                import production.make_extra_data_dirs.make_extraData_dirs as medd
                # 创建 ani/flo 的 extra_data_dirs, 在最开始创建，避免权限问题22
                medd.make_rough_lay_extra_data_dirs(self.dialog.version_dir)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

