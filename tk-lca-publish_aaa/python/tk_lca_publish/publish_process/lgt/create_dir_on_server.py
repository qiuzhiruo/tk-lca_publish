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

            if self.dialog.publish_mode:
                if not os.path.isdir(self.dialog.version_dir+'/katana'):
                    os.makedirs(self.dialog.version_dir + '/katana')

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

