# -*- coding: utf-8 -*-
# @Time    : 18-7-30 上午11:44
# @Author  : zhangzheng
__author__ = 'zhangzheng'
__maintainer__ = 'zhangzheng'



import os
import traceback

import pymel.core as pm

ASSETSPATH = ['/asset/crd/']


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"资产路径检查。"
        self.description = u"资产路径必须是群集资产路径。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            rns = pm.ls(rf=1)
            errs = []
            for rn in rns:
                file_path = pm.referenceQuery(rn, f=1)
                check_true = False
                for check_path in ASSETSPATH:
                    if check_path in file_path:
                        check_true = True
                if not check_true:
                    errs.append(str(rn))
            if len(errs) == 0:
                return ''
            else:
                out_text = ','.join(errs)
                return u'以下资产reference文件路径错误请替换为指定的群集资产，\n\t%s' % out_text
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
