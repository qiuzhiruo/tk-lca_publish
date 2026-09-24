# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import os
import traceback
import shutil

import pymel.core as pm


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"释放镜头锁"
        self.description = u"释放镜头的sg_shot_owner属性值"
        return

    def proceed(self):
        try:
            # check if the shot owner should be changed
            import gene.shot_owner_funcs.functions as funcs_sof
            reload(funcs_sof)
            show_owner = funcs_sof.Funcs()
            show_owner.release_shot_lock(force = True)
            
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


