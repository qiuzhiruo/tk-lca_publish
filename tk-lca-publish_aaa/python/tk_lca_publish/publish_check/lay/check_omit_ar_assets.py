# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import os
import sys

import pymel.core as pm

import check_omit_assets as coa;reload(coa)

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查omit的AR资产。"
        self.description = u"制作过程中 PM 会放弃使用一些资产，需要把它们排查出来。"
        self.auto_fix = False
        self.duty = u"项目管理。"
        return


    def run_check(self):

        try:
            if 'd_omit_assets' not in self.dialog.__dict__:
                coa.get_omit_assets(self.dialog)
            
            omit_assets = {}
            ars = pm.ls(type = 'assemblyReference')
            for ar in ars:
                asset_name = ar.name().split(':')[-1].replace('_AR', '').rstrip('1234567890')
                if self.dialog.d_omit_assets.has_key(asset_name):
                    omit_assets[ar.name()] = str(self.dialog.d_omit_assets[asset_name]['id'])
            
            if omit_assets:
                pattern = u'发现AR资产 %s 是已经废弃/omt 的资产 (id: %s)\n'
                msg = ''
                for omit_asset in omit_assets:
                    msg += pattern % (omit_asset, omit_assets[omit_asset])
                return msg
            
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

