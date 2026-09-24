# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Huang Xin
#
# Date: 2018.10
#
# Description: As the description shows below
#
############################################

import os
import traceback
import shutil
import cfx.cfx_auto_pipeline.state_check as sck
import cfx.cfx_felt_pipeline.hair_pass_utils as hpu
# All system check classes will use StdCheck as the class name.


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查所选cache目录的完整性"
        self.description = u""
        self.auto_fix = True
        self.duty = u"艺术家本人"
        self.check_result = {}
        self.publish_dir = None
        return


    def run_check(self):
        try:
            # scene_ver = int(self.dialog.version_num)
            # scene_ver_str = self.dialog.version_num
            # version_key = self.dialog.version_key
            proj = self.dialog.project['name'].lower()
            shot = self.dialog.entity['name']
            
            n_cache_items = self.dialog.w_publish_file.listWidget_cache.count()
            if n_cache_items is 0:
                if hpu.check_hair_pass_exists(proj, shot):
                    return ""
                return u"没有选择cache。"

            check_cache = sck.ShotOperation(proj, shot)
            check_cache.constant_tasks = [self.dialog.task['name'].lower()]
            need_publish = check_cache.check_cache_status()

            update_info = {}
            for i in range(n_cache_items):
                cache_dir = self.dialog.w_publish_file.listWidget_cache.item(i).text()
                if cache_dir.endswith('/'):
                    cache_dir = cache_dir[:-1]
                self.publish_dir = cache_dir + '/cache'
                for asset in os.listdir(cache_dir + '/cache'):
                    update_info.setdefault(asset, cache_dir + '/cache/' + asset)

            msg = "\n"
            assets_dir = need_publish.values()[0]
            for asset_dir in assets_dir:
                asset = asset_dir.split('/')[-1]
                if asset not in update_info.keys():
                    self.check_result.setdefault(asset, asset_dir)
                    msg += asset + ': ' + asset_dir + '\n'


            if not self.check_result:
                return ""

            msg = u'%s\n请检查以上cache是否需要publish，若不需要请跳过该检查或清理掉多余cache重新检查，若需要请点击自动修复补全到最新版本文件夹'%msg
            return msg

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        print(self.check_result.items())
        for asset, asset_dir in self.check_result.items():
            shutil.move(asset_dir, os.path.join(self.publish_dir, asset))
            publishPath = os.path.join(self.publish_dir, asset)
            self.web_publish(publishPath)
        self.check_result = {}
        return ''

    def web_publish(self,publishPath):
        replace = publishPath
        proj = publishPath.split('/')[4]
        shot = publishPath.split('/')[7]
        for root, dirs, files in os.walk(publishPath):
            new_root = root.split('/cache/')[0]
            for fileFullName in files:
                if fileFullName.endswith('xgen'):
                    realPath = root + '/' + fileFullName
                    old_data = []
                    with open(realPath, 'r') as f:
                        old_data.extend(f.readlines())
                    with open(realPath, 'w') as f:
                        for line in old_data:
                            lineList = line.split()
                            if len(lineList) > 1:
                                if lineList[0] == 'cacheFileName':
                                    orient = lineList[1].split('/cache/')[0]
                                    if orient.split('/')[1] == 'output' or '/mnt/output/' in orient:
                                        print('Old xg cacheFileName:',orient)
                                        print('New xg cacheFileName:',new_root)
                                        line = line.replace(orient, new_root)
                            f.write(line)

                if fileFullName.endswith('xml'):
                    realPath = root + '/' + fileFullName
                    old_data = []
                    with open(realPath, 'r') as f:
                        old_data.extend(f.readlines())
                    with open(realPath, 'w') as f:
                        for line in old_data:
                            if len(line.split()) > 2:
                                if line.split()[1] == 'name=\"data\"':
                                    for str in line.split():
                                        if len(str.split('/')) > 2:
                                            if str.split('/')[1] == 'output' or '/mnt/output/' in str:
                                                orient = str.split('/cache/')[0]
                                                print('Old xml cacheFileName:',orient)
                                                print('New xml cacheFileName:',new_root)
                                                line = line.replace(orient, new_root)
                                elif '/output/' in line:
                                    if line.split('"')[-2].startswith('/mnt/output/') or line.split('"')[-2].startswith(
                                            '/output/'):
                                        orient = line.split('"')[-2].split('/cache/')[0]
                                        print('Old xml cacheFileName:',orient)
                                        print('New xml cacheFileName:',new_root)
                                        line = line.replace(orient, new_root)
                            f.write(line)



    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


