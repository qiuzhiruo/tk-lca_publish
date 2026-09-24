# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.05
#
# Description:
#
############################################

import traceback
import subprocess


DC_MAP = {'Animation':('olivia', 'lucy', ),
          'Layout':('xuyang', 'xiaotian')}

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查mov文件起始结束帧。"
        self.description = u"检查mov文件起始结束帧。Downstream Publish必须和Shotgun上时间一致。 Daily Publish如果时间和shotgun不一致，必须有组长的相关note。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            for data in self.dialog.shots_preview_data:
                try:
                    i = data['preview_info'].index('Comment')
                except:
                    i = data['preview_info'].index('Movie/Comment')
                f_range_str = data['preview_info'][i+1]
                f_range = f_range_str.split('-')
                cut_in = f_range[0]
                cut_out = f_range[1]

                result = u'镜头: ' + data['shot_info']['code'] + u', '
                if not len(f_range) == 2:
                    return result+u"无法从 mov 文件获取有效的起始结束帧: " + data['preview_info'][i+1]

                if not cut_in.isdigit():
                    return result+u"无效的起始帧: " + cut_in

                if not cut_out.isdigit():
                    return result+u"无效的结束帧: " + cut_out

                if not 'Duration' in data['preview_info']:
                    return result+u"无法获得预览内的实际时长。请用 LCA Tools 中 Playblaster 工具拍屏。"

                i = data['preview_info'].index('Duration')
                duration = data['preview_info'][i+1]
                if not duration.isdigit():
                    return result+u"无效的预览时长: " + duration

                if int(duration) != int(cut_out) - int(cut_in) + 1:
                    return result+u"预览实际时长: " + duration + u"帧，与记录时长: " + f_range_str + u"不匹配。"

                shot = self.dialog.sg.find_one('Shot',
                                               [['id', 'is', data['shot_info']['id']]],
                                               ['sg_cut_in', 'sg_cut_out', 'sg_ani_cut_in', 'sg_ani_cut_out'])
                
                if shot['sg_ani_cut_in'] and shot['sg_ani_cut_out']:
                    if data['cut_in'] != shot['sg_ani_cut_in'] or data['cut_out'] != shot['sg_ani_cut_out']:
                        if data['cut_in'] != shot['sg_cut_in'] or data['cut_out'] != shot['sg_cut_out']:
                            return result+u"帧范围和shotgun上的sg_cut_in/out 和 sg_ani_cut_in/out均不一致, 请检查!\n镜头范围："+ \
                                   str(data['cut_in']) + u' to '+ str(data['cut_out']) + \
                                   u"\nShotgun剪辑范围：" + str(shot['sg_cut_in']) + u' to '+ str(shot['sg_cut_out']) +\
                                   u"\nShotgun动画范围：" + str(shot['sg_ani_cut_in']) + u' to '+ str(shot['sg_ani_cut_out'])
                        else:
                            return result+u"帧范围和shotgun上的 sg_ani_cut_in/out不一致, 请检查!\n镜头范围："+ \
                                   str(data['cut_in']) + u' to '+ str(data['cut_out']) + \
                                   u"\nShotgun剪辑范围：" + str(shot['sg_cut_in']) + u' to '+ str(shot['sg_cut_out']) +\
                                   u"\nShotgun动画范围：" + str(shot['sg_ani_cut_in']) + u' to '+ str(shot['sg_ani_cut_out'])
                else:
                    if data['cut_in'] != shot['sg_cut_in'] or data['cut_out'] != shot['sg_cut_out']:
                        return result+u"帧范围和shotgun上不一致，同时也没有发现sg_ani_cut_in/out, 请检查!\n镜头范围："+ \
                               str(data['cut_in']) + u' to '+ str(data['cut_out']) + \
                               u"\nShotgun范围："+str(shot['sg_cut_in'])+ u' to '+str(shot['sg_cut_out'])

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

