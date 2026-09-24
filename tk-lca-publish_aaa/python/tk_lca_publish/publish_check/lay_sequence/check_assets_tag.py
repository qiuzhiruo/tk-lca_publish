# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.07
#
# Description:
#
############################################

import traceback
import subprocess
import datetime

import pymel.core as pm

import lay.lca_camera_sequencer.functions as functions_cs


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查镜头资产关系是否已标记，且标记时间在3小时之内."
        self.description = u"检查场景内是否存在命名为'<镜头号>_assets'的objectSet。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            self.invalid_shots = []
            self.invalid_times = []
            for data in self.dialog.shots_preview_data:
                result = functions_cs.get_tagged_assets(data['shot_info']['code'])
                if result is None:
                    self.invalid_shots.append(data['shot_node'])
                else:
                    shot_objSet = data['shot_info']['code'].lower() + functions_cs.ASSETS_SUFFIX
                    if pm.attributeQuery('add_tag_time', node = shot_objSet, exists = True):
                        record_time = pm.getAttr(shot_objSet + '.add_tag_time')
                        record_datetime = datetime.datetime.strptime(record_time, '%Y-%m-%d %H:%M:%S')
                        crnt_datetime = datetime.datetime.strptime(str(datetime.datetime.now())[:19], '%Y-%m-%d %H:%M:%S')
                        if crnt_datetime - record_datetime > datetime.timedelta(0, 3600 * 3):       # 3 hours
                            self.invalid_times.append(data['shot_info']['code'])

            if self.invalid_shots:
                return u'镜头资产关系不正确，请使用自动修复功能并核对结果。'
            
            if self.invalid_times:
                msg = '\n'.join(self.invalid_times)
                return u'以下镜头的objectSet标记时间过于久远，请艺术家重新标记\n' \
                       u'（标记方法：Camera Manager ->选择镜头号->右键 Tag Assets in Use）：\n' + msg

            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        for shot in self.invalid_shots:
            functions_cs.tag_assets_in_use(shot)
        return ""

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
