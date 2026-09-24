# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.08
#
# Description: 
#
############################################

import traceback

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 Edt 使用的版本时长是否和 shotgun 上镜头长一致"
        self.description = u"检查 Edt 使用的版本时长是否和 shotgun 上镜头长一致"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            l_unmatched = []
            for shot_name in self.dialog.d_shot_versions.keys():
                v_name = self.dialog.d_shot_versions[shot_name].keys()[0]
                v_length = self.dialog.d_shot_versions[shot_name][v_name]['frame_count']
                s_length = self.dialog.d_shot_versions[shot_name][v_name]['entity.Shot.sg_cut_duration']
                if v_length != s_length:
                    l_unmatched.append( u"版本 " + v_name + u" 的时长(" + str(v_length) + u") 和镜头时(" + str(s_length) + u")长不一致")

            return u"\n".join(l_unmatched)
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

