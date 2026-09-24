# -*- coding:utf-8 -*-
import os
########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.09
#
# Description: 
#
########################################################################################

import traceback
import pymel.core as pm
import datetime as dt
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"确保模型法线被检查过。"
        self.description = u"法线检查工具会在master节点上留下时间记号，我们要确保publish之前模型被检查过。"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return


    @record_time(__file__)
    def run_check(self):
        try:

            if pm.objExists('master.normal_check_stamp'):
                now = dt.datetime.now()
                stamp_time = pm.Attribute('master.normal_check_stamp').get()
                stamp_datetime = dt.datetime.strptime(stamp_time, '%Y-%m-%d %H:%M:%S')
                timedelta = now - stamp_datetime
                if timedelta.seconds//60 > 15 or timedelta.days != 0:
                    self.run_fix()

            else:
                self.run_fix()

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            import sys
            # sys.path.append("U:/toolset/tools/mod")
            # sys.path.append("/mnt/utility/toolset/tools/mod")
            toolset = os.getenv('LC_TOOLSET')
            sys.path.append(os.path.join(toolset, 'tools'))
            from mod.model_checks import check
            reload(check)
            check.main()
            return ''

        except:
            return traceback.format_exc()
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


