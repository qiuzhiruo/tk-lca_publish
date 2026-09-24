# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"不可以reference rra,scn 类型的资产"
        self.description = u"不可以reference rra,scn 类型的资产"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            ref_file = pm.listReferences()
            master_ref_file = ''
            try:
                master_ref_file = str(pm.FileReference('|master').path).replace('\\', '/')
            except:
                pass
            illegal_ref = []
            for r in ref_file:
                path = str(r.path).replace('\\', '/')
                if '/rra/' in path or '/scn/' in path:
                    if master_ref_file and path == master_ref_file:
                        # top master is a reference, skip it
                        continue
                    illegal_ref.append( r.namespace )

            if illegal_ref:
                return u"发现rra或scn类型的资产:\n" + '\n'.join( illegal_ref )

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


