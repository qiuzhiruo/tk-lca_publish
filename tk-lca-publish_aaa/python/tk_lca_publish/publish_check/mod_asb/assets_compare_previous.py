# -*- coding:utf-8 -*-
__author__ = 'lvyuedong'

import traceback

import os
import re
import pymel.core as pm

import sys
toolset = os.getenv('LC_TOOLSET')
sys.path.append( '%s/tools/gene/scene_operator' % toolset)
import sceneOperator as scnOp
reload(scnOp)

import production.pipeline.mayaReferenceUtils as mru
reload(mru)

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产引用是否和上一版本一致。"
        self.description = u"检查当前场景的资产是否和上一版本保持一致，此为警告信息。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            # get assets from xml of previous publish
            assets_previous_raw = scnOp.XmlParser(project=self.dialog.project['name']).getAssetsNameFromAsbXml( self.dialog.entity['name'] )
            # get assets from current scene
            assets_current_raw = mru.MayaReferenceUtils().listMasters('|master')

            assets_previous = set([i for i in assets_previous_raw.iterkeys()])
            assets_current = set([str(i).replace(':master', '') for i in assets_current_raw])

            if not assets_previous <= assets_current:
                return u"与上一版本相比，少了以下资产:\n" + '\n'.join( assets_previous.difference(assets_current) )

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


