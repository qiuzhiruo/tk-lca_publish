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
import re
import shutil


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查子资产状态和版本"
        self.description = u"检查子资产的文件夹是否存在，之前有没有publish版本"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            self.l_existing = []
            self.l_missing = []

            tokens = self.dialog.publish_root.split('/')
            i = tokens.index('asset')
            asset_root = '/'.join(tokens[:i+1])

            for asset_name, asset in self.dialog.hyperloop.iteritems():
                if self.dialog.hyperloop[asset_name]["group"] == "shotgun":
                    version_add_num = 0
                else:
                    version_add_num = 1

                asset['v_name'] = asset_name + '.mod.model.v001'
                for v in self.dialog.sg.find('Version', [['entity', 'is', asset], ['code', 'contains', '.mod.model.v']], ['code']):
                    tokens = v['code'].split('.')
                    if tokens[3][1:].isdigit():
                        asset['v_name'] = asset_name + '.mod.model.v%03d' % (int(tokens[3][1:]) + version_add_num)

                publish_dir = asset_root + '/' + asset['sg_asset_type'] + '/' + asset_name + '/mod/publish/'
                asset['v_dir'] = publish_dir + asset['v_name'] + '/'

                if not os.path.isdir(publish_dir):
                    self.l_missing.append(publish_dir)

                if os.path.isdir(asset['v_dir']) and self.dialog.hyperloop[asset_name]["group"] != "shotgun":
                    self.l_existing.append(asset['v_dir'])

            if len(self.l_missing) > 0:
                return u"publish文件夹没建：\n" + '\n'.join(self.l_missing)

            if len(self.l_existing) > 0:
                return u"有之前publish失败的版本文件夹需要删除：\n" + '\n'.join(self.l_existing)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            for v_dir in self.l_missing:
                if not os.path.isdir(v_dir):
                    os.makedirs(v_dir)

            for v_dir in self.l_existing:
                if os.path.isdir(v_dir):
                    shutil.rmtree(v_dir)
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

