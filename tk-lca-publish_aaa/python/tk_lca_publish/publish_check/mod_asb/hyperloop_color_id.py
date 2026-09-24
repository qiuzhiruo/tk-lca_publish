# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2019 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.06
#
############################################

import traceback
import os
import proc.set_asset_color_id as sci

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查子资产 color id"
        self.description = u"检查子资产的 color id"
        self.auto_fix = True
        self.duty = u"TD"
        return


    def run_check(self):

        try:
            l_invalid_assets = []
            for asset_name, asset in self.dialog.hyperloop.iteritems():
                a_info = self.dialog.sg.find_one('Asset', [['id', 'is', asset['id']]], ['sg_color_id', 'sg_asset_type'])
                asset['sg_color_id'] = a_info['sg_color_id']
                if asset['sg_asset_type'] == "asb":
                    continue
                if asset['sg_color_id'] is None or asset['sg_color_id'] == '0 0 0':
                    l_invalid_assets.append(asset_name)

            if len(l_invalid_assets) > 0:
                return u"资产 %s 没有 color id" % (', '.join(l_invalid_assets))
            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            for asset_name, asset in self.dialog.hyperloop.iteritems():
                if asset['sg_color_id'] is None or asset['sg_color_id'] == '0 0 0':
                    update_color_id = sci.set_color_id(self.dialog.project['name'], asset_name, self.dialog.sg)
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

