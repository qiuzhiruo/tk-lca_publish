# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import os
import traceback
import shutil
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"删除安全边框。"
        self.description = u"删除安全边框。"
        return

    def proceed(self):
        try:
            try:
                safearea = pm.ls(type='spReticleLoc')
                for s in safearea:
                    pm.delete(s.getParent())
            except:
                pass

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
