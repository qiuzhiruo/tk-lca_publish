# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description:
#
############################################

import traceback
import subprocess


COMMON_PATTERNS = ['Comment', 'Info', 'Movie/Comment']

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查mov文件起始结束帧。"
        self.description = u"检查mov文件起始结束帧。Downstream Publish必须和Shotgun上时间一致。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:

            cmt_str = None
            for cmt_p in COMMON_PATTERNS:
                if cmt_p in self.dialog.l_mov_info:
                    cmt_str = cmt_p
                    break
            if cmt_str is None:
                return u"无法获得预览内的 Comment 信息。请用 LCA Tools 中 Playblaster 工具拍屏。"


            i = self.dialog.l_mov_info.index(cmt_str)
            f_range_str = self.dialog.l_mov_info[i + 1]
            f_range = f_range_str.split('-')
            if not len(f_range) == 2:
                return u"无法从 mov 文件获取有效的起始结束帧: " + self.dialog.l_mov_info[i +1 ]

            try:
                cut_in = int(float(f_range[0]))
            except:
                return u"无效的起始帧: " + f_range[0]

            try:
                cut_out = int(float(f_range[1]))
            except:
                return u"无效的结束帧: " + f_range[1]

            if not 'Duration' in self.dialog.l_mov_info:
                return u"无法获得预览内的实际时长。请用 LCA Tools 中 Playblaster 工具拍屏。"

            i = self.dialog.l_mov_info.index('Duration')
            try:
                duration = float(self.dialog.l_mov_info[i+1])
            except:
                return u"无效的预览时长: " + self.dialog.l_mov_info[i+1]

            if int(duration) != cut_out - cut_in + 1:
                return u"预览实际时长: %s帧，与记录时长: %s不匹配。"%(duration, f_range_str)

            shot = self.dialog.sg.find_one('Shot', [['id', 'is', self.dialog.entity['id']]], ['sg_cut_in', 'sg_cut_out', 'sg_cut_duration', 'sg_ani_cut_in', 'sg_ani_cut_out'])

            if shot['sg_ani_cut_in'] is not None and shot['sg_ani_cut_out'] is not None and self.dialog.step['name'] in ['lay', 'ani', 'flo']:
                sg_cut_in = shot['sg_ani_cut_in']
                sg_cut_out = shot['sg_ani_cut_out']
                cut_fields = 'Ani Cut In/Out'
            else:
                sg_cut_in = shot['sg_cut_in']
                sg_cut_out = shot['sg_cut_out']
                cut_fields = 'Cut In/Out'

            if cut_in != sg_cut_in or cut_out != sg_cut_out:
                # for some ani test seq, we auto fix the frame range in sg base on mov frame range
                if self.dialog.step['name'] == 'ani' and self.dialog.entity['name'][:3] in ['z88']:
                    self.dialog.sg.update('Shot', self.dialog.entity['id'], {'sg_cut_in': cut_in, 'sg_cut_out': cut_out, 'sg_cut_duration': int(duration)})
                    print '[NOTICE] Update "{}" cut in out to: "{}"-"{}"'.format(self.dialog.entity['name'], cut_in, cut_out)
                else:
                    return (u"预览的 mov 文件的帧范围和shotgun上不一致，请检查!\n"
                            u"mov 文件范围：%s to %s\n"
                            u"Shotgun上 %s 范围：%s to %s\n"
                            u"请找组长或者镜头负责的pc协调，找剪辑重新Publish帧范围或者调整 %s。")%(cut_in, cut_out, cut_fields, sg_cut_in, sg_cut_out, cut_fields)

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

