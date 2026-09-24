# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.07
#
# Description:
#
############################################

import traceback


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查镜头 Ani Cut In/Out 和 Cut In/Out 是否一致。"
        self.description = u"Cut In/Out 是剪辑的时间点，Ani Cut In/Out 是动画的时间点，如果不一致，说明剪辑还没有对镜头时长做出最终决定，这个时候Publish可能会给下游组错误的时长。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:

            shot = self.dialog.sg.find_one('Shot', [['id', 'is', self.dialog.entity['id']]], ['sg_cut_in', 'sg_cut_out', 'sg_cut_duration', 'sg_ani_cut_in', 'sg_ani_cut_out'])

            if shot['sg_ani_cut_in'] is not None and shot['sg_ani_cut_out'] is not None:
                if shot['sg_ani_cut_in'] != shot['sg_cut_in'] or shot['sg_ani_cut_out'] != shot['sg_cut_out']:
                    return(u"Shotgun 上 Cut In/Out 和 Ani Cut In/Out 不一致，说明这个镜头剪辑还没有决定最终时长。\n"
                           u"Cut In/Out 范围：%s - %s\n"
                           u"Ani Cut In/Out 范围：%s - %s\n"
                           u"请找组长或者镜头负责的pc协调，找剪辑重新Publish帧范围或者调整 Ani Cut In/Out。")%(shot['sg_cut_in'], shot['sg_cut_out'], shot['sg_ani_cut_in'], shot['sg_ani_cut_out'])

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

