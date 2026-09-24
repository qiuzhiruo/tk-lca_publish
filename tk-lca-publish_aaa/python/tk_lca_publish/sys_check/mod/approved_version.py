# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.08
#
# Description: 
#
########################################################################################

import traceback
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"有通过的版本才能做 Downstream Publish。"
        self.description = u"粗/精模 Downstream publish, 都必须对应的(daily)版本通过, 才能做 Donwstream Publish。\n换句话说，不能一上来第一次publish就做 Downstream Publish."
        self.auto_fix = False
        self.duty = u"艺术家本人,部门组长和项目协调。"
        return


    def run_check(self):
        try:
            no_approved = True

            l_versions = self.dialog.sg.find('Version', [['sg_task', 'is', self.dialog.task]], ['code', 'sg_version_type', 'tag_list', 'sg_status_list'])
            for v_info in l_versions:
                if v_info['sg_status_list'] == 'apr' and self.dialog.version_tag.encode('utf-8') in v_info['tag_list']:
                    self.dialog.print_log(u"本资产有 " + self.dialog.version_tag + u" 版本通过")
                    no_approved = False

            # If the parent asset mod version is approved, the sub asset is allowed to publish downstream.
            if no_approved:
                asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id'] ]], ['parents'])
                for parent in asset['parents']:
                    l_versions = self.dialog.sg.find('Version', [['code', 'contains', '.mod.'], ['entity', 'is', parent]], ['code', 'sg_version_type', 'tag_list', 'sg_status_list'])
                    for v_info in l_versions:
                        if v_info['sg_status_list'] == 'apr' and self.dialog.version_tag.encode('utf-8') in v_info['tag_list']:
                            self.dialog.print_log(u"父资产 " +parent['name']+ u" 有 " + self.dialog.version_tag + u" 版本通过")
                            no_approved = False

            if no_approved:
                return u'之前还没有本资产或父资产的 ' + self.dialog.version_tag + u' 版本(Daily 版本)被通过，这种情况下模型不能做 Downstream Publish。'

            return ''

        except:
            return traceback.format_exc()
    

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


