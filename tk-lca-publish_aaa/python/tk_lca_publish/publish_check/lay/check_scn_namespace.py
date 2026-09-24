# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import traceback

import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():
    """
        dependency: check_hierarchy
    """
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"scene资产的命名空间应该为空"
        self.description = u"scene资产的命名空间应该为空，即':'"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            for ref in pm.system.getReferences().items():
                ns = ref[0]
                file_ref = ref[1]
                if '.scn.' in os.path.basename( str(file_ref.path) ):
                    if ns != ':':
                        return u"scene资产的命名空间应该为空，现在为: "+ns
            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



