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
        self.process_name = u"删除安全边框"
        self.description = u"删除安全边框"
        return

    def findSafeAreaNodes(self, ns=''):
        safearea = pm.ls(ns + '*layout_safearea*')
        if safearea:
            return self.findSafeAreaNodes(ns + '*:')
        return safearea

    def proceed(self):
        try:

            reticles = pm.ls(type='spReticleLoc')
            for r in reticles:
                pm.delete(r.getParent())

            safearea = self.findSafeAreaNodes()
            if safearea:
                for s in safearea:
                    pm.delete(s)

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
