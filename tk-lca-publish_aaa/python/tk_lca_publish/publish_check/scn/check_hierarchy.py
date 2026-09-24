# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查scene资产的层级命名。"
        self.description = u"scene资产最上层组为master"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        try:
            if not pm.objExists("|master"):
                return u"没有找到最高层的 |master 组。"

            all_obj = []
            for node_type in ['mesh', 'transform', 'assemblyReference', 'locator']:
                all_obj.extend(pm.ls(type=node_type))

            cam_list = ['|persp', '|side', '|top', '|front']
            
            err_list=[]
            for obj in all_obj:
                if not obj.fullPath().startswith('|master'):
                    if obj.fullPath() in cam_list or  obj.fullPath().startswith('|cam'):
                        continue
                    print obj.fullPath()
                    err_list.append(obj.fullPath())
                    
            if err_list:
                pm.select(err_list)
                return u"|master 组 外有多余的物体。"+u','.join(err_list)
            
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


