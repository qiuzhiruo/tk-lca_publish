# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"assets组外的物体应该删除或放入|assets|lay组下"
        self.description = u"assets组外的物体应该删除或放入|assets|lay组下"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            dags = [ d for d in pm.ls(assemblies=True) if str(d) not in ['persp', 'top', 'front', 'side', 'assets', 'cameras'] ]
            dags = [ str(d) for d in dags if not d.isReferenced() and pm.nodeType(d) in ['transform', 'mesh', 'nurbsSurface'] ]

            for d in dags[:]:
                if 'fosterParent' in d:
                    try:
                        dags.remove(d)
                    except:
                        pass

            if dags:
                return u"The following objects should be put into |assets|lay group:\n" + '\n'.join(dags)

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


