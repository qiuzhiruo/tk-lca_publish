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
        self.process_name = u"删除unloaded资产。"
        self.description = u"删除unloaded资产。"
        return

    def proceed(self):
        try:
            ref_files = pm.listReferences()
            for r in ref_files:
                try:
                    if not r.isLoaded():
                        r.remove()
                except:
                    print traceback.format_exc()

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
