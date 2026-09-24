# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yu Huazhuo
#
# Date: 2019.04
#

########################################################################################
import sys
import re
import os
import traceback
import pymel.core as pm
import glob
from proc.function_running_time import record_time


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查角色相机。"
        self.description = u"chr asm crd 资产必须最少导出一版相机。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            mod_asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]],
                                                ['code', 'sg_asset_type'])
            
            if not mod_asset['sg_asset_type'] in ['chr','asm','crd']:
                print 'mod_asset : ',mod_asset
                return ""

            if pm.objExists('turntable_cam'):
                cam_list = pm.listRelatives('turntable_cam', c=True)
                if len(cam_list) != 2:
                    return u'turntable_cam 组下相机数量不对'

            transform_list = pm.ls(type="transform")

            if "turntable_cam" not in transform_list:

                for list_t in transform_list:

                    fine = re.match("turntable_cam[0-9a-zA-Z_]*", str(list_t))
                    if fine:
                        turntable_name = fine.group()

                        if turntable_name != "turntable_cam":
                            pm.select(turntable_name)

                            return u"turntable相机的组命名错误"+turntable_name+u"，请把组的名字改为turntable_cam"

                    if list_t == "body_cam_group":
                        get_parent = list_t.getParent()
                        if get_parent != "turntable_cam":

                            return u"turntable相机的组命名错误" + get_parent + u"，请把组的名字改为turntable_cam"

            cam_publish_glob_str = 'Z:/projects/{0}/asset/{1}/{2}/mod/publish/*/turntable_cam/head_cam.abc'.format(
                self.dialog.project['name'].lower(), mod_asset['sg_asset_type'], mod_asset['code'])

            if sys.platform.startswith('linux'):
                cam_publish_glob_str = cam_publish_glob_str.replace('Z:/', '/mnt/proj/')

            cam_files = glob.glob(cam_publish_glob_str)

            if cam_files:
                print 'cam_files : ', cam_files
                return ""

            cam_work_glob_str = 'W:/projects/{0}/asset/{1}/{2}/mod/task/maya/images/turntable/*/head_cam.abc'.format(
                self.dialog.project['name'].lower(), mod_asset['sg_asset_type'], mod_asset['code'])

            if sys.platform.startswith('linux'):
                cam_work_glob_str = cam_work_glob_str.replace('W:/', '/mnt/work/')

            cam_files = glob.glob(cam_work_glob_str)

            if cam_files:
                print 'cam_files : ', cam_files
                return ""

            error_info = u"chr crd asm 资产需要有一版相机供下游使用。 \n且需要自己创建后确认相机镜头是否合适。 \n"
            if not pm.objExists('|turntable_cam|body_cam_group|body_cam|body_camShape'):
                print 'not find  body_cam ...'
                return error_info+u" 未找到 body_cam ..."

            if not pm.objExists('|turntable_cam|head_cam_group|head_cam|head_camShape'):
                print 'not find  head_cam ...'
                return error_info+u" 未找到 head_cam ..."

            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            self.fix_copy_cam()
            return ''
        except:
            return traceback.format_exc()

    def fix_copy_cam(self):
        if pm.objExists('|pasted__turntable_cam'):
            pm.rename('|pasted__turntable_cam', 'turntable_cam')
        for cam in pm.listRelatives('|turntable_cam', ad=True):
            new_name = cam.name().replace('pasted__', '')
            cam.rename(new_name)

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty


