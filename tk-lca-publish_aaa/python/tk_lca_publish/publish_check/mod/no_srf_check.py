# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: Check to see if any vertice are overlapping to each other.
#
########################################################################################

import traceback
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as om
import production.pipeline.lcProdProj as lcp
import re
from proc.function_running_time import record_time
# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"当没有材质版本时的模型检查项"
        self.description = u"当没有开始材质制作的时候，需要模型进行一些检查"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            asset = self.dialog.entity['name'].lower()
            proj = self.dialog.project['name'].lower()
            localP=lcp.lcProdProj()
            localP.setProj(proj)
            self.dialog.has_srf=True
            if localP.getSrfAsset(asset):
                Klf_path=localP.getSrfAsset(asset).get("klf",None)
                if not Klf_path or "srf.surfacing.v000" in Klf_path:
                    self.dialog.has_srf=False
            else:
                self.dialog.has_srf=False
            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''

        try:
            pass
            return ''

        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


