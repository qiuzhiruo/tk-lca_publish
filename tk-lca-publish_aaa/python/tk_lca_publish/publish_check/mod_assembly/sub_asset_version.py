# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description: 
#
########################################################################################

import traceback
import sys
import os

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"确认将要publish的子资产任务信息和版本。"
        self.description = u"确认将要publish的子资产任务信息和版本。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:

            for asset_name in self.dialog.d_assets_info.keys():
                
                asset = self.dialog.d_assets_info[asset_name]['asset']
                task = self.dialog.d_assets_info[asset_name]['task']
                t_info = self.dialog.sg.find_one('Task', [['id', 'is', task['id']]], ['sg_status_list'])
                if not t_info['sg_status_list']:
                    return u"资产 " + asset_name + u' 的 model 任务状态为空。'

                if t_info['sg_status_list'] in ['omt', 'fin']:
                    return u"资产 " + asset_name + u' 的 model 任务状态已经 ' + t_info['sg_status_list']

                l_sg_versions = self.dialog.sg.find('Version', [['project', 'is', self.dialog.project], ['entity', 'is', asset], ['sg_task', 'is', task]], ['code', 'sg_version_type'] )
                self.dialog.d_assets_info[asset_name]['sg_versions'] = l_sg_versions

                v_max = sg_v_max = 0
                publish_dir = self.dialog.d_assets_info[asset_name]['publish_dir']
                l_versions = sorted(os.listdir(publish_dir))

                for version in l_versions:
                    if not (version.startswith(asset_name + '.mod.model.v') and len(version) == len(asset_name)+15 and version[-3:].isdigit()):
                        continue

                    v_max = int(version[-3:])

                for version in l_sg_versions:
                    if not version['code'][-3:].isdigit():
                        continue
                    sg_v_max = max(sg_v_max, int(version['code'][-3:]))

                self.dialog.d_assets_info[asset_name]['version_name'] = asset_name + ('.mod.model.v%03d' % (max(v_max, sg_v_max)+1))
                self.dialog.d_assets_info[asset_name]['version_dir'] = publish_dir + '/' + self.dialog.d_assets_info[asset_name]['version_name']
                print self.dialog.d_assets_info[asset_name]['version_dir']
                self.dialog.d_assets_info[asset_name]['tank_file'] = publish_dir + '/' + self.dialog.d_assets_info[asset_name]['version_name'] + '/' + asset_name + '.ma'
                
                work_dir = publish_dir.replace('/proj/','/work/').replace('Z:','W:').replace('/publish','/task')
                import glob
                file_list = glob.glob(os.path.join(work_dir, 'maya',asset_name + '.mod.model.*.ma' ))
                if file_list:
                    file_list.sort()
                    work_ver = int((file_list[-1].rsplit('.',2)[1]).split('v')[-1])+1
                    work_file = os.path.join(work_dir, 'maya',asset_name + '.mod.model.v{:0>3d}.ma'.format(work_ver))
                else:
                    work_file = os.path.join(work_dir, 'maya', asset_name + '.mod.model.v001.ma')
                self.dialog.d_assets_info[asset_name]['work_file'] = work_file

                
                
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


