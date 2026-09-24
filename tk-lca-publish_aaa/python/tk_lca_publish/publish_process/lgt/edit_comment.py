# -*- coding:utf-8 -*-
__author__ = 'yingjie'

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Copy publish files
#
############################################

import os
import traceback


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"如果是 Rough lgt 版本，修改版本描述"
        self.description = u"保证Rough lgt版本描述开头为：本版本仅供组内审核"
        return


    def proceed(self):
        if self.dialog.version_tag =='Rough lgt':
            if not self.dialog.description.startswith(u"本版本仅供组内审核。资产非最终状态。灯光，颜色均未通过sup审核。"):
                self.dialog.description = u"本版本仅供组内审核。资产非最终状态。灯光，颜色均未通过sup审核。" + self.dialog.description

        return ''

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
