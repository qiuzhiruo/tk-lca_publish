# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: lin zhu
#
# Date: 2014.05
#
# Description: 
#
############################################

import traceback
import os
import pymel.core as pm
import re


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查reference文件和nameSpace名称是否统一。"
        self.description = u"如果reference 文件是*/shentu_cleaning.ma，其名称空间应该是shentu_cleaningRN或者shentu_cleaningRN1"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        strs = u''
        try:
            get_wrong_dict = self.findWrongNameSpace()
            if len(get_wrong_dict.keys()):
                for item in get_wrong_dict.items():
                    strs += u'目前是%s--->应该为%s\n' % (item[0], item[1])

                return u'以下名称空间不一致\n' + strs
            else:
                return ''

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            input_dict = self.findWrongNameSpace()
            self.replaceRefNamespace(input_dict)
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

    def findWrongNameSpace(self):
        no_match_dict = {}
        for ref in pm.system.getReferences().items():
            currentNameSpace = ref[0]
            ref_file = str(ref[1])
            if '{' in os.path.basename(ref_file):
                num = re.findall("{(\d+)}", ref_file)[0]
                right_name_space = os.path.splitext(os.path.basename(ref_file))[0] + num
            else:
                right_name_space = os.path.splitext(os.path.basename(ref_file))[0]
            if right_name_space != currentNameSpace:
                if re.findall("(\D+)", currentNameSpace)[0] != re.findall("(\D+)", right_name_space)[0]:
                    no_match_dict[currentNameSpace] = right_name_space

        return no_match_dict

    def replaceRefNamespace(self, input_dict):
        if len(input_dict.keys()) > 0:
            for item in input_dict.items():
                old_name_space = item[0]
                new_name_space = item[1]
                try:
                    pm.system.namespace(ren=(old_name_space, new_name_space))
                except:
                    print u'namespace 需要手动修复'

        pm.system.saveFile(f=1)
