# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.08
#
# Description:
#
############################################
import traceback
import tank
import sys
import os
import pymel.core as pm

import lay.lca_camera_lock.functions as functions_cl;

reload(functions_cl)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"引用新提交的摄像机并释放所有权。"
        self.description = u"删除导入的摄像机，引用并锁定新版摄像机，释放Shotgun上镜头摄像机的所有权。"
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
            log = 'reload_latest_camera.py\n'

            if self.dialog.is_camera_published and not functions_cl.is_camera_locked():
                if self.dialog.step['name'] not in ['ani', 'flo']:
                    functions_cl.relock_camera(need_confirm=False)
                else:
                    functions_cl.relock_camera(need_confirm=False, raw=False)
                log += 'relock camera successfully\n'
            else:
                log += 'there is no need to reload camera\n'

            self.write_log(log)

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
