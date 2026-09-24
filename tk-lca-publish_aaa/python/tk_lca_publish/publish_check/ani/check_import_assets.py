# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.09
#
# Description: Check imported assets
#
############################################

import traceback

import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"资产不可以import进场景。"
        self.description = u"所有资产不可以import进场景。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            imported_assets = []
            masters = pm.ls('master', recursive=True)
            for m in masters:
                isinstance(m, pm.nt.Transform)
                if m.isReferenced():
                    continue

                parent = m.getParent()
                if parent and parent.nodeType() == 'assemblyReference':
                    continue

                if m.isChildOf('|assets|lay'):
                    continue

                name = m.longName()
                imported_assets.append(name)
            if imported_assets:
                return u"所有资产必须是reference，以下资产是import:\n" + '\n'.join(imported_assets)
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
