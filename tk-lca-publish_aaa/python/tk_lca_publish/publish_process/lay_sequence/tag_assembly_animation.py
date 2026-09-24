# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import os
import traceback

import callback_save.secure_file as secure_file;reload(secure_file)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"给已k动画的AR资产做标记。"
        self.description = u"已k过动画的AR资产，会在shotgun的资产tag_list属性上标记为ani_lock， 模型组在做修改时不允许改变其命名和层级。"
        return


    def proceed(self):
        try:
            secure_file.check_assembly_animation()

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

