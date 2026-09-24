# -*- coding:utf-8 -*-
import traceback

import pymel.core as pm
import maya.mel as mel


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"还原优化ANI Publish Process的maya设置修改"
        self.description = u"还原在ani_publish_begin_set.py中优化Publish Process的maya设置修改"
        return

    def proceed(self):
        try:
            # 还原MG动画备份约束设置
            if self.dialog.old_mg_real_time_save_setting == 1:
                mel.eval('turnOnOffAnimRescueAutoSaveInMinitoolBox 0 1;')

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
