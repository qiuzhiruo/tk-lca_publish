# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.12
#
# Description: 
#
############################################

import traceback
import os

import pymel.core as pm

import sys


import production.pipeline.mayaReferenceUtils as mru
reload(mru)


def get_omit_assets(dialog):
    """
    """
    l_assets = dialog.sg.find('Asset', [['project', 'is', dialog.project]], ['sg_asset_type', 'sg_status_list', 'code'])

    # sometimes a pc creates more than one asset with the same name by mistake, but she just keeps one of them and omits the others.
    # we have to figure out these assets...
    assets_count_dict = {}
    for asset in l_assets:
        if asset['code'] not in assets_count_dict:
            assets_count_dict[asset['code']] = 1
        else:
            assets_count_dict[asset['code']] += 1

    dialog.d_omit_assets = {}
    dialog.d_dup_assets = {}
    for asset in l_assets:
        if asset['sg_status_list'] == 'omt':
            dialog.d_omit_assets[asset['code']] = asset
        if assets_count_dict[asset['code']] > 1:
            dialog.d_dup_assets[asset['code']] = asset

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查omit的reference资产。"
        self.description = u"制作过程中 PM 会放弃使用一些资产，需要把它们排查出来。"
        self.auto_fix = False
        self.duty = u"项目管理。"
        return


    def run_check(self):
        try:
            if 'd_omit_assets' not in self.dialog.__dict__:
                get_omit_assets(self.dialog)
            
            omit_assets = {}
            dup_assets = []
            l_masters = mru.MayaReferenceUtils().listMasters(top='|assets', asb=False, scene=False)
            for master in l_masters:
                asset_name = master.name().split(':')[0].rstrip('1234567890')
                if self.dialog.d_omit_assets.has_key(asset_name):
                    omit_assets[master.name()] = str(self.dialog.d_omit_assets[asset_name]['id'])
                if self.dialog.d_dup_assets.has_key(asset_name):
                    dup_assets.append(master.name())
            msg = ''
            if omit_assets:
                pattern = u'发现reference资产 %s 是已经废弃/omt 的资产 (id: %s)\n'
                for omit_asset in omit_assets:
                    msg += pattern % (omit_asset, omit_assets[omit_asset])

            if dup_assets:
                msg += u'发现SG上的重命资产,需要PC先纠正资产重命问题:\n{}'.join('\n'.join(dup_assets))

            return msg

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

