# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import os
import pymel.core as pm
import lay.lca_check_ar_scale.main as main;reload(main)

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查文件中的Assembly Reference的缩放'
        self.description = u'scn类型的AR节点不应有缩放/asb, env只能是uniform scale'
        self.auto_fix = True
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:
            if self.dialog.entity['name'].startswith('z'):
                return u''
            
            self.ar_scale_dict = main.get_scaled_ars()
            if self.ar_scale_dict:
                msg = u'以下AR节点有缩放值：\n'
                for ar_scale in self.ar_scale_dict:
                    msg += str(ar_scale) + ' ' + str(self.ar_scale_dict[ar_scale]) + '\n'
                return msg
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            main.fix_scaled_ars(self.ar_scale_dict)
        except:
            return traceback.format_exc()
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

