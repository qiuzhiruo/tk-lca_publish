# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Proceed layout publish files
#
############################################

import os
import traceback
import shutil
import pymel.core as pm


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"提交layout文件。"
        self.description = u"提交layout文件到服务器。"
        return

    def write_log(self, content):
        try:
            import proc.log_publish_process as lpp
            reload(lpp)
            current_file = pm.sceneName().replace('\\', '/')
            log_file = os.path.dirname(current_file) + '/publish_log/' + os.path.basename(current_file)[
                                                                         :-3] + '.log.txt'
            log_file = log_file.replace('//', '/')
            lpp.log(log_file, content)
        except:
            pass

    def proceed(self):
        try:
            log = 'publish_lay_files.py\n'

            ma_file = str(pm.saveFile())
            log += 'saved current scene\n'
            self.dialog.tank_file = self.dialog.version_dir + '/' + os.path.basename(ma_file)
            log += 'self.dialog.tank_file: ' + self.dialog.tank_file + '\n'
            if os.path.isfile(ma_file):
                shutil.copyfile(ma_file, self.dialog.tank_file)
                log += 'copy file from ' + ma_file + ' to ' + self.dialog.tank_file + '\n'

            self.write_log(log)

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
