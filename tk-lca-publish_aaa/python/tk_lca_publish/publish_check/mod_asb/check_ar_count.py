# -*- coding:utf-8 -*-


import traceback
import os
import maya.cmds as cmds
import maya.mel as mel
import json
import pymel.core as pm
import maya.api.OpenMaya as om
import production.pipeline.lcProdProj as lcp
import re
import sys
from xml.etree import ElementTree
import tempfile

import publish_process.gen.sgXml_parser as sgxml


class StdCheck:
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查ar的数量是否超过六千个。"
        self.description = u"检查ar的数量是否超过六千个。skip tag: skip_ar_check"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        asset_info = self.dialog.sg.find_one("Asset",[['project', 'is', self.dialog.project],
                                                      ['code', 'is', self.dialog.entity['name']]],
                                             ['sg_asset_type', 'tag_list'])


        if 'skip_ar_check' in asset_info['tag_list']:
            return ''

        if len(pm.ls(type='assemblyReference')) > 6000:
            return 'AR 的数量已经超过六千个。请尽量缩减。 无法缩减可找组长加tag： skip_ar_check'

        return ''

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
