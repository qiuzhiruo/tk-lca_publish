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

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"镜头的 cut in/ cut out 是否有效。"
        self.description = u"镜头的 cut in/ cut out 应该是一些整数。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            #self.dialog.w_publish_file.tableWidget_shots
            for shot_name, shot_info in self.dialog.d_seq_shots.iteritems():
                shot_info['edl_cut_in'] = ''
                shot_info['edl_cut_out'] = ''

            for i in range(self.dialog.w_publish_file.tableWidget_shots.rowCount()):
                shot_item = self.dialog.w_publish_file.tableWidget_shots.item(i,0)
                cut_in_item = self.dialog.w_publish_file.tableWidget_shots.item(i,3)
                cut_out_item = self.dialog.w_publish_file.tableWidget_shots.item(i,4)
                if shot_item and cut_in_item and cut_out_item:
                    shot_name = str(shot_item.text())
                    cut_in = str(cut_in_item.text())
                    cut_out = str(cut_out_item.text())
                    if not cut_in.isdigit():
                        return u"镜头 " + shot_name + u" 有错误的 cut in : " + cut_in 

                    if not cut_out.isdigit():
                        return u"镜头 " + shot_name + u" 有错误的 cut out : " + cut_out

            return ""

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


