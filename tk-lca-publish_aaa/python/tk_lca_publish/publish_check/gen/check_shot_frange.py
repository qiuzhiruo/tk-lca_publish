# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import traceback

import os
import re
import pymel.core as pm
import sys

# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查镜头的帧范围是否和shotgun一致。"
        self.description = u"检查镜头的帧范围是否和shotgun一致。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:

            cut_in = int(pm.animation.playbackOptions(q=True, minTime=True))
            cut_out = int(pm.animation.playbackOptions(q=True, maxTime=True))

            shot = self.dialog.sg.find_one('Shot', [['id', 'is', self.dialog.entity['id']]], ['sg_cut_in', 'sg_cut_out', 'sg_cut_duration', 'sg_ani_cut_in', 'sg_ani_cut_out'])
            edt_cut_in = shot['sg_cut_in'] 
            edt_cut_out = shot['sg_cut_out'] 
            
            if shot['sg_ani_cut_in'] is not None and shot['sg_ani_cut_out'] is not None and self.dialog.step['name'] in ['ani', 'flo']:
                sg_cut_in = shot['sg_ani_cut_in']
                sg_cut_out = shot['sg_ani_cut_out']
                cut_fields = 'Ani Cut In/Out'
            else:
                sg_cut_in = shot['sg_cut_in']
                sg_cut_out = shot['sg_cut_out']
                cut_fields = 'Cut In/Out'

            if cut_in == sg_cut_in and  sg_cut_in == sg_cut_out:
                if cut_out == sg_cut_out +1:
                    return ""

            if cut_in != sg_cut_in or cut_out != sg_cut_out:
                return (u"当前文件的帧范围和shotgun上不一致，请检查!\n"
                        u"mov 文件范围：%s to %s\n"
                        u"Shotgun上 %s 范围：%s to %s\n"
                        u"请找组长或者镜头负责的pc协调，找剪辑重新Publish帧范围或者调整 %s。") % (cut_in, cut_out, cut_fields, sg_cut_in, sg_cut_out, cut_fields)
            
            if self.dialog.task['name'] == 'animation':
                d_v_type = {0:'Daily', 1:'Checked', 2:'Downstream'}
            else:
                d_v_type = {0:'Daily', 1:'Downstream'}
            publish_mode = d_v_type[self.dialog.publish_mode]
            if publish_mode == 'Downstream' and self.dialog.version_tag != u'测试':
                if sg_cut_in != edt_cut_in or sg_cut_out != edt_cut_out:
                    return (u"Downstream除去测试外必须和剪辑时间一致！\n"
                            u"当前文件的帧范围和shotgun上剪辑时长不一致，请检查!\n"
                            u"mov 文件范围：%s to %s\n"
                            u"Shotgun上 剪辑范围：%s to %s\n"
                            u"请找组长或者镜头负责的pc协调，找剪辑重新Publish帧范围或者调整剪辑时长。") % (cut_in, cut_out, edt_cut_in, edt_cut_out)
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



