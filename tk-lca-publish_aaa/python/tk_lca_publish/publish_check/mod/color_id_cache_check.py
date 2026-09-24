# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: ZHAO JIAYI
#
# Date: 2017.09
#
# Description: check color id
#
############################################

import traceback
import pymel.core as pm
import sys
# sys.path.insert(0,'/mnt/public/Share/zhaojiayi/gitrepo/tk-lca-publish/python/tk_lca_publish')
import proc.set_asset_color_id as sci
reload (sci)
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否有color id cache。"
        self.description = u"提交下游的文件需要提供color id 。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        try:

            for asset_name in self.dialog.d_assets_info.keys():
                asset_color_id_str = sci.get_color_id(self.dialog.project['name'], asset_name, self.dialog.sg)
                print asset_color_id_str
                if asset_color_id_str == "0 0 0" or asset_color_id_str == None :
                    return u" 没有color id " 
                else:
                    return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                update_color_id = sci.set_color_id(self.dialog.project['name'], asset_name, self.dialog.sg)
            if update_color_id =="0 0 0" or update_color_id == None:
                print u" 没有color id "
            else:
                return ""
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



