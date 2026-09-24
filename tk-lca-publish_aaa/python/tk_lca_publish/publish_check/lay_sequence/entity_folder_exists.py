# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.06
#
# Description: Check folder existence
#
############################################

import traceback

import os

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查所选镜头的publish文件夹是否建立。"
        self.description = u"在服务器上，应该已经建立了这个场/镜头/资产所用的，各个部门的publish文件夹。"
        self.auto_fix = False
        self.duty = u"流程管理。"
        return


    def run_check(self):
        try:
            template = self.dialog.tk.templates['maya_seq_work']
            fields = self.dialog.ctx.as_template_fields(template)
            template = self.dialog.tk.templates['shot_publish']
            for data in self.dialog.shots_preview_data:
                fields.update(Shot=data['shot_info']['code'])
                data['publish_root'] = template.apply_fields(fields)
                if not os.path.isdir(data['publish_root']):
                    return (u"Publish文件夹没有建立: " + data['publish_root'])

                self.dialog.print_log('Pulbish to: ' + data['publish_root'])
            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        return ""


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

